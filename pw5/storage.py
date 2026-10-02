import gzip
import json
from pathlib import Path

from pw5.domains import Course, Mark, Student


STUDENTS_FILE = Path(__file__).with_name("students.txt")
COURSES_FILE = Path(__file__).with_name("courses.txt")
MARKS_FILE = Path(__file__).with_name("marks.txt")
ARCHIVE_FILE = Path(__file__).with_name("students.dat")


def save_data(students, courses, marks):
    data = {
        "students": [student.__dict__ for student in students],
        "courses": [course.__dict__ for course in courses],
        "marks": [mark.__dict__ for mark in marks],
    }
    collections = (
        (STUDENTS_FILE, data["students"]),
        (COURSES_FILE, data["courses"]),
        (MARKS_FILE, data["marks"]),
    )
    for data_file, items in collections:
        with data_file.open("w", encoding="utf-8") as file:
            json.dump(items, file, indent=2)

    with gzip.open(ARCHIVE_FILE, "wt", encoding="utf-8") as file:
        json.dump(data, file)


def _load_marks(items):
    marks = []
    for item in items:
        mark_data = dict(item)
        if "scale" not in mark_data:
            mark_data["value"] *= 2
            mark_data["scale"] = 20
        marks.append(Mark(**mark_data))
    return marks


def load_data():
    data_files = (STUDENTS_FILE, COURSES_FILE, MARKS_FILE)
    if ARCHIVE_FILE.exists():
        with gzip.open(ARCHIVE_FILE, "rt", encoding="utf-8") as file:
            data = json.load(file)
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