import gzip
import json
from pathlib import Path

from pw5.domains import Course, Mark, Student


STUDENTS_FILE = Path(__file__).with_name("students.txt")
COURSES_FILE = Path(__file__).with_name("courses.txt")
MARKS_FILE = Path(__file__).with_name("marks.txt")
LEGACY_DATA_FILE = Path(__file__).with_name("students.dat")


def save_data(students, courses, marks):
    collections = (
        (STUDENTS_FILE, students),
        (COURSES_FILE, courses),
        (MARKS_FILE, marks),
    )
    for data_file, items in collections:
        with data_file.open("w", encoding="utf-8") as file:
            json.dump([item.__dict__ for item in items], file, indent=2)


def load_data():
    data_files = (STUDENTS_FILE, COURSES_FILE, MARKS_FILE)
    if any(data_file.exists() for data_file in data_files):
        collections = []
        for data_file in data_files:
            if data_file.exists():
                with data_file.open("r", encoding="utf-8") as file:
                    collections.append(json.load(file))
            else:
                collections.append([])
        students_data, courses_data, marks_data = collections
    elif not LEGACY_DATA_FILE.exists():
        return [], [], []
    else:
        with gzip.open(LEGACY_DATA_FILE, "rt", encoding="utf-8") as file:
            data = json.load(file)
        students_data = data["students"]
        courses_data = data["courses"]
        marks_data = data["marks"]

    students = [Student(**item) for item in students_data]
    courses = [Course(**item) for item in courses_data]
    marks = [Mark(**item) for item in marks_data]
    return students, courses, marks