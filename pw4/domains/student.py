import numpy as np


class Student:
    def __init__(self, student_id, name, dob):
        self.student_id = student_id
        self.name = name
        self.dob = dob

    def calculate_gpa(self, marks, courses):
        marks_list = []
        credits_list = []

        for mark in marks:
            if mark.student_id == self.student_id:
                for course in courses:
                    if course.course_id == mark.course_id:
                        marks_list.append(mark.value)
                        credits_list.append(course.credits)

        if len(marks_list) == 0:
            return None

        marks_array = np.array(marks_list)
        credits_array = np.array(credits_list)
        return np.sum(marks_array * credits_array) / np.sum(credits_array)