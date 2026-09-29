import gzip
import json
from pathlib import Path

from pw5.domains import Course, Mark, Student


DATA_FILE = Path(__file__).with_name("students.dat")


def save_data(students, courses, marks):
    data = {
        "students": [student.__dict__ for student in students],
        "courses": [course.__dict__ for course in courses],
        "marks": [mark.__dict__ for mark in marks],
    }

    with gzip.open(DATA_FILE, "wt", encoding="utf-8") as file:
        json.dump(data, file)


def load_data():
    if not DATA_FILE.exists():
        return [], [], []

    with gzip.open(DATA_FILE, "rt", encoding="utf-8") as file:
        data = json.load(file)

    students = [Student(**item) for item in data["students"]]
    courses = [Course(**item) for item in data["courses"]]
    marks = [Mark(**item) for item in data["marks"]]
    return students, courses, marks