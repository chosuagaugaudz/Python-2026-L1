import math

from pw5.domains import Course, Mark, Student


def input_students():
    students = []
    count = int(input("Number of students: "))

    for i in range(count):
        print("Student", i + 1, ":")
        student_id = input("  ID: ")
        name = input("  Name: ")
        dob = input("  Date of birth (dd/mm/yyyy): ")
        students.append(Student(student_id, name, dob))

    return students


def input_courses():
    courses = []
    count = int(input("Number of courses: "))

    for i in range(count):
        print("Course", i + 1, ":")
        course_id = input("  ID: ")
        name = input("  Name: ")
        credits = int(input("  Credits: "))
        courses.append(Course(course_id, name, credits))

    return courses


def input_marks(students, course_id):
    marks = []

    for student in students:
        raw_mark = input(
            "  Mark for " + student.name + " (" + student.student_id + "): "
        )
        raw_mark = float(raw_mark.replace(",", "."))
        value = math.floor(raw_mark * 10) / 10
        marks.append(Mark(student.student_id, course_id, value))

    return marks