from pw4.input import input_courses, input_marks, input_students
from pw4.output import (
    list_courses,
    list_students,
    show_gpa_ranking,
    show_marks_for_course,
)


def menu():
    students = []
    courses = []
    marks = []

    while True:
        print()
        print("1. Input students")
        print("2. Input courses")
        print("3. Input marks for a course")
        print("4. List courses")
        print("5. List students")
        print("6. Show marks for a course")
        print("7. Show GPA ranking (curses)")
        print("0. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            students.extend(input_students())
        elif choice == "2":
            courses.extend(input_courses())
        elif choice == "3":
            list_courses(courses)
            course_id = input("Enter course ID to input marks for: ")
            marks.extend(input_marks(students, course_id))
        elif choice == "4":
            list_courses(courses)
        elif choice == "5":
            list_students(students)
        elif choice == "6":
            show_marks_for_course(students, courses, marks)
        elif choice == "7":
            show_gpa_ranking(students, courses, marks)
        elif choice == "0":
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    menu()