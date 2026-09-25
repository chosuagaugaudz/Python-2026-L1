student_ids = []
student_names = []
student_dobs = []

course_ids = []
course_names = []

mark_student_ids = []   # parallel lists: mark i belongs to
mark_course_ids = []    # student mark_student_ids[i], course mark_course_ids[i]
mark_values = []        # with value mark_values[i]


def input_students():
    n = int(input("Number of students: "))
    for i in range(n):
        print("Student", i + 1, ":")
        sid = input("  ID: ")
        name = input("  Name: ")
        dob = input("  Date of birth (dd/mm/yyyy): ")
        student_ids.append(sid)
        student_names.append(name)
        student_dobs.append(dob)


def input_courses():
    n = int(input("Number of courses: "))
    for i in range(n):
        print("Course", i + 1, ":")
        cid = input("  ID: ")
        name = input("  Name: ")
        course_ids.append(cid)
        course_names.append(name)


def input_marks():
    list_courses()
    cid = input("Enter course ID to input marks for: ")

    for i in range(len(student_ids)):
        sid = student_ids[i]
        name = student_names[i]
        mark = float(input("  Mark for " + name + " (" + sid + "): "))
        mark_student_ids.append(sid)
        mark_course_ids.append(cid)
        mark_values.append(mark)


def list_courses():
    print()
    print("-- Courses --")
    for i in range(len(course_ids)):
        print(course_ids[i], "-", course_names[i])


def list_students():
    print()
    print("-- Students --")
    for i in range(len(student_ids)):
        print(student_ids[i], "-", student_names[i], "-", student_dobs[i])


def show_marks_for_course():
    list_courses()
    cid = input("Enter course ID: ")

    print()
    print("-- Marks for course", cid, "--")
    for i in range(len(student_ids)):
        sid = student_ids[i]
        name = student_names[i]
        mark_found = False
        for j in range(len(mark_student_ids)):
            if mark_student_ids[j] == sid and mark_course_ids[j] == cid:
                print(sid, "-", name, "-", mark_values[j])
                mark_found = True
        if not mark_found:
            print(sid, "-", name, "-", "no mark yet")


def menu():
    while True:
        print()
        print("1. Input students")
        print("2. Input courses")
        print("3. Input marks for a course")
        print("4. List courses")
        print("5. List students")
        print("6. Show marks for a course")
        print("0. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            input_students()
        elif choice == "2":
            input_courses()
        elif choice == "3":
            input_marks()
        elif choice == "4":
            list_courses()
        elif choice == "5":
            list_students()
        elif choice == "6":
            show_marks_for_course()
        elif choice == "0":
            break
        else:
            print("Invalid option.")


menu()