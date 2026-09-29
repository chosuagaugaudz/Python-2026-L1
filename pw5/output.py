import curses


def list_courses(courses):
    print()
    print("-- Courses --")
    for course in courses:
        print(course.course_id, "-", course.name, "-", course.credits, "credits")


def list_students(students):
    print()
    print("-- Students --")
    for student in students:
        print(student.student_id, "-", student.name, "-", student.dob)


def show_marks_for_course(students, courses, marks):
    list_courses(courses)
    course_id = input("Enter course ID: ")

    print()
    print("-- Marks for course", course_id, "--")
    for student in students:
        mark_found = False
        for mark in marks:
            if mark.student_id == student.student_id and mark.course_id == course_id:
                print(student.student_id, "-", student.name, "-", mark.value)
                mark_found = True
        if not mark_found:
            print(student.student_id, "-", student.name, "-", "no mark yet")


def list_students_by_gpa(students, courses, marks):
    results = []
    for student in students:
        results.append((student, student.calculate_gpa(marks, courses)))

    results.sort(key=lambda result: (result[1] is None, -(result[1] or 0)))
    return results


def show_gpa_ranking_curses(stdscr, students, courses, marks):
    stdscr.clear()
    results = list_students_by_gpa(students, courses, marks)
    stdscr.addstr(0, 2, "GPA RANKING (descending)", curses.A_BOLD)
    stdscr.addstr(1, 2, "-" * 40)

    row = 3
    for rank, (student, gpa) in enumerate(results, start=1):
        if gpa is None:
            line = f"{rank:>2}. {student.name} ({student.student_id}) - no marks yet"
        else:
            line = f"{rank:>2}. {student.name} ({student.student_id}) - GPA: {gpa:.2f}"
        stdscr.addstr(row, 2, line)
        row += 1

    stdscr.addstr(row + 1, 2, "Press any key to return to menu...")
    stdscr.refresh()
    stdscr.getch()


def show_gpa_ranking(students, courses, marks):
    curses.wrapper(show_gpa_ranking_curses, students, courses, marks)