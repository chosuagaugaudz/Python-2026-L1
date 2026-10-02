class Student:
    def __init__(self, student_id, name, dob):
        self.student_id = student_id
        self.name = name
        self.dob = dob

    def calculate_gpa(self, marks, courses):
        weighted_total = 0
        total_credits = 0
        has_marks = False

        for mark in marks:
            if mark.student_id == self.student_id:
                for course in courses:
                    if course.course_id == mark.course_id:
                        mark_scale = getattr(mark, "scale", 20)
                        weighted_total += (mark.value / mark_scale * 10) * course.credits
                        total_credits += course.credits
                        has_marks = True

        if not has_marks or total_credits == 0:
            return None

        return weighted_total / total_credits