import gzip
import json
import pickle
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from threading import Lock

from pw8.domains import Course, Mark, Student


STUDENTS_FILE = Path(__file__).with_name("students.txt")
COURSES_FILE = Path(__file__).with_name("courses.txt")
MARKS_FILE = Path(__file__).with_name("marks.txt")
ARCHIVE_FILE = Path(__file__).with_name("students.dat")

_SAVE_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="pw8-save")
_PENDING_SAVES = []
_PENDING_LOCK = Lock()


class StorageError(RuntimeError):
    pass


def _write_data(data):
    temporary_file = ARCHIVE_FILE.with_name(ARCHIVE_FILE.name + ".tmp")
    try:
        with gzip.open(temporary_file, "wb") as archive:
            pickle.dump(data, archive, protocol=pickle.HIGHEST_PROTOCOL)
        temporary_file.replace(ARCHIVE_FILE)
    finally:
        if temporary_file.exists():
            temporary_file.unlink()


def save_data(students, courses, marks) -> Future:
    data = {
        "students": [dict(student.__dict__) for student in students],
        "courses": [dict(course.__dict__) for course in courses],
        "marks": [dict(mark.__dict__) for mark in marks],
    }
    with _PENDING_LOCK:
        future = _SAVE_EXECUTOR.submit(_write_data, data)
        _PENDING_SAVES.append(future)
    return future


def wait_for_saves():
    with _PENDING_LOCK:
        pending_saves = tuple(_PENDING_SAVES)
        _PENDING_SAVES.clear()

    failures = []
    for future in pending_saves:
        failure = future.exception()
        if failure is not None:
            failures.append(failure)
    if failures:
        raise StorageError("A background data save failed.") from failures[0]


def shutdown_storage():
    try:
        wait_for_saves()
    finally:
        _SAVE_EXECUTOR.shutdown(wait=True)


def _load_marks(items):
    marks = []
    for item in items:
        mark_data = dict(item)
        if "scale" not in mark_data:
            mark_data["value"] *= 2
            mark_data["scale"] = 20
        marks.append(Mark(**mark_data))
    return marks


def _load_archive():
    with gzip.open(ARCHIVE_FILE, "rb") as archive:
        contents = archive.read()

    if contents.lstrip().startswith(b"{"):
        return json.loads(contents.decode("utf-8"))
    return pickle.loads(contents)


def load_data():
    wait_for_saves()
    data_files = (STUDENTS_FILE, COURSES_FILE, MARKS_FILE)
    if ARCHIVE_FILE.exists():
        data = _load_archive()
        students_data = data["students"]
        courses_data = data["courses"]
        marks_data = data["marks"]
    elif any(data_file.exists() for data_file in data_files):
        collections = []
        for data_file in data_files:
            if data_file.exists():
                with data_file.open("r", encoding="utf-8") as file:
                    collections.append(json.load(file))
            else:
                collections.append([])
        students_data, courses_data, marks_data = collections
    else:
        return [], [], []

    students = [Student(**item) for item in students_data]
    courses = [Course(**item) for item in courses_data]
    marks = _load_marks(marks_data)
    return students, courses, marks
