import os

from pw5.input import input_courses, input_marks, input_students
from pw5.output import (
    list_courses,
    list_students,
    show_gpa_ranking,
    show_marks_for_course,
)
from pw5.storage import load_data, save_data


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def wait_for_menu():
    print("\nPress any key to return to the menu...", end="", flush=True)
    if os.name == "nt":
        import msvcrt

        msvcrt.getch()
    else:
        input()


def menu():
    students, courses, marks = load_data()

    while True:
        clear_screen()
        print()
        print("1. Input students")
        print("2. Input courses")
        print("3. Input marks for a course")
        print("4. List courses")
        print("5. List students")
        print("6. Show marks for a course")
        print("7. Show GPA ranking (curses)")
        print("8. Delete a list")
        print("0. Save and exit")

        choice = input("Choose an option: ")

        if choice == "1":
            students.extend(input_students())
            save_data(students, courses, marks)
        elif choice == "2":
            courses.extend(input_courses())
            save_data(students, courses, marks)
        elif choice == "3":
            list_courses(courses)
            course_id = input("Enter course ID to input marks for: ")
            marks.extend(input_marks(students, course_id))
            save_data(students, courses, marks)
        elif choice == "4":
            clear_screen()
            list_courses(courses)
            wait_for_menu()
        elif choice == "5":
            clear_screen()
            list_students(students)
            wait_for_menu()
        elif choice == "6":
            clear_screen()
            show_marks_for_course(students, courses, marks)
            wait_for_menu()
        elif choice == "7":
            clear_screen()
            show_gpa_ranking(students, courses, marks)
        elif choice == "8":
            print("1. Delete students and their marks")
            print("2. Delete courses and their marks")
            print("3. Delete marks")
            delete_choice = input("Choose a list to delete (0 to cancel): ")

            if delete_choice == "1":
                confirmed = input("Delete all students and their marks? (y/n): ")
                if confirmed.strip().lower() == "y":
                    students.clear()
                    marks.clear()
                    save_data(students, courses, marks)
                    print("Students and their marks deleted.")
            elif delete_choice == "2":
                confirmed = input("Delete all courses and their marks? (y/n): ")
                if confirmed.strip().lower() == "y":
                    course_ids = {course.course_id for course in courses}
                    courses.clear()
                    marks[:] = [mark for mark in marks if mark.course_id not in course_ids]
                    save_data(students, courses, marks)
                    print("Courses and their marks deleted.")
            elif delete_choice == "3":
                confirmed = input("Delete all marks? (y/n): ")
                if confirmed.strip().lower() == "y":
                    marks.clear()
                    save_data(students, courses, marks)
                    print("Marks deleted.")
            elif delete_choice != "0":
                print("Invalid option.")
        elif choice == "0":
            save_data(students, courses, marks)
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    menu()