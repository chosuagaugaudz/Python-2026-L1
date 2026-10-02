import csv
import io
import json
from datetime import datetime
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import RLock
from urllib.parse import unquote, urlsplit

from pw5.domains import Course, Mark, Student
from pw5.storage import load_data, save_data


STATIC_DIR = Path(__file__).with_name("static")
DATA_LOCK = RLock()


class ApiError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


def _required_text(payload, field):
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field.replace('_', ' ').title()} is required.")
    return value.strip()


def _required_date(payload, field):
    value = _required_text(payload, field)
    try:
        datetime.strptime(value, "%d/%m/%Y")
    except ValueError as error:
        raise ValueError("Date of birth must be a real date in DD/MM/YYYY format.") from error
    return value


def _import_date(value):
    value = value.strip()
    if not value:
        return ""
    for date_format in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, date_format).strftime("%d/%m/%Y")
        except ValueError:
            continue
    raise ValueError("Use DD/MM/YYYY for dates of birth.")


def _prepare_student_import(content, existing_students):
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Choose a non-empty CSV or text file.")
    try:
        rows = list(csv.reader(io.StringIO(content)))
    except csv.Error as error:
        raise ValueError("The import file is not valid CSV.") from error
    rows = [row for row in rows if any(cell.strip() for cell in row)]
    if not rows:
        raise ValueError("The import file has no student rows.")

    aliases = {
        "name": {"name", "full_name", "student_name"},
        "student_id": {"student_id", "id", "student_number", "student_code"},
        "dob": {"dob", "date_of_birth", "birth_date"},
    }
    headers = [cell.strip().lower().replace(" ", "_").replace("-", "_") for cell in rows[0]]
    header_map = {
        field: next((index for index, header in enumerate(headers) if header in names), None)
        for field, names in aliases.items()
    }
    has_header = any(index is not None for index in header_map.values())
    if has_header and header_map["name"] is None:
        raise ValueError("The CSV needs a name column.")
    if has_header:
        data_rows = rows[1:]
    else:
        data_rows = rows
        if any(len(row) > 1 for row in data_rows):
            raise ValueError("Add a header row before CSV columns, or use one name per line.")

    used_ids = {student.student_id for student in existing_students}
    imported = []
    skipped = []
    errors = []
    generated = 0
    next_number = 1

    for row_number, row in enumerate(data_rows, start=2 if has_header else 1):
        name = row[header_map["name"]].strip() if has_header and header_map["name"] < len(row) else (row[0].strip() if row else "")
        if not name:
            skipped.append(f"Row {row_number}: name is blank.")
            continue
        student_id = ""
        dob = ""
        generated_id = False
        if has_header:
            id_index = header_map["student_id"]
            dob_index = header_map["dob"]
            student_id = row[id_index].strip() if id_index is not None and id_index < len(row) else ""
            raw_dob = row[dob_index] if dob_index is not None and dob_index < len(row) else ""
        else:
            raw_dob = ""

        if not student_id:
            while f"STU-{next_number:04d}" in used_ids:
                next_number += 1
            student_id = f"STU-{next_number:04d}"
            next_number += 1
            generated_id = True
        if student_id in used_ids:
            skipped.append(f"Row {row_number}: student ID {student_id} already exists.")
            continue
        try:
            dob = _import_date(raw_dob)
        except ValueError as error:
            errors.append(f"Row {row_number}: {error}")
            continue

        used_ids.add(student_id)
        generated += int(generated_id)
        imported.append({"student_id": student_id, "name": name, "dob": dob})

    return {
        "students": imported,
        "generated": generated,
        "skipped": skipped,
        "errors": errors,
    }


class StudentAppHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError) as error:
            raise ValueError("Request body must be valid JSON.") from error
        if not isinstance(payload, dict):
            raise ValueError("Request body must be a JSON object.")
        return payload

    def _api_error(self, error):
        status = error.status if isinstance(error, ApiError) else 400
        self._send_json(status, {"error": str(error)})

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/data":
            with DATA_LOCK:
                students, courses, marks = load_data()
                self._send_json(
                    200,
                    {
                        "students": [student.__dict__ for student in students],
                        "courses": [course.__dict__ for course in courses],
                        "marks": [mark.__dict__ for mark in marks],
                    },
                )
            return
        if path.startswith("/api/"):
            self._send_json(404, {"error": "API endpoint not found."})
            return
        super().do_GET()

    def do_POST(self):
        parts = [unquote(part) for part in urlsplit(self.path).path.strip("/").split("/")]
        try:
            payload = self._read_json()
            with DATA_LOCK:
                students, courses, marks = load_data()

                if parts == ["api", "students", "import", "preview"]:
                    preview = _prepare_student_import(payload.get("content"), students)
                    self._send_json(200, preview)
                    return
                elif parts == ["api", "students", "import"]:
                    imported = _prepare_student_import(payload.get("content"), students)
                    if not imported["students"]:
                        raise ApiError(400, "No students are ready to import.")
                    students.extend(Student(**student) for student in imported["students"])
                    save_data(students, courses, marks)
                    self._send_json(201, imported)
                    return
                elif parts == ["api", "students"]:
                    student_id = _required_text(payload, "student_id")
                    if any(student.student_id == student_id for student in students):
                        raise ApiError(409, "That student ID already exists.")
                    student = Student(
                        student_id,
                        _required_text(payload, "name"),
                        _required_date(payload, "dob"),
                    )
                    students.append(student)
                    created = student.__dict__
                elif parts == ["api", "courses"]:
                    course_id = _required_text(payload, "course_id")
                    if any(course.course_id == course_id for course in courses):
                        raise ApiError(409, "That course ID already exists.")
                    credits = payload.get("credits")
                    if isinstance(credits, bool) or not isinstance(credits, int) or credits <= 0:
                        raise ValueError("Credits must be a positive whole number.")
                    course = Course(
                        course_id,
                        _required_text(payload, "name"),
                        credits,
                    )
                    courses.append(course)
                    created = course.__dict__
                elif parts == ["api", "marks"]:
                    student_id = _required_text(payload, "student_id")
                    course_id = _required_text(payload, "course_id")
                    student_ids = {student.student_id for student in students}
                    course_ids = {course.course_id for course in courses}
                    if student_id not in student_ids:
                        raise ValueError("Choose an existing student.")
                    if course_id not in course_ids:
                        raise ValueError("Choose an existing course.")
                    if any(
                        mark.student_id == student_id and mark.course_id == course_id
                        for mark in marks
                    ):
                        raise ApiError(409, "A mark already exists for that student and course.")
                    try:
                        scale = int(payload.get("scale", 20))
                    except (TypeError, ValueError) as error:
                        raise ValueError("Marks must use the 20-point scale.") from error
                    if scale not in (10, 20):
                        raise ValueError("Marks must use the 20-point scale.")
                    try:
                        value = float(str(payload.get("value", "")).replace(",", "."))
                    except ValueError as error:
                        raise ValueError("Mark must be a number from 0 to 20.") from error
                    if not 0 <= value <= scale:
                        raise ValueError(f"Mark must be between 0 and {scale}.")
                    if scale == 10:
                        value *= 2
                    value = int(value * 10) / 10
                    mark = Mark(student_id, course_id, value, 20)
                    marks.append(mark)
                    created = mark.__dict__
                else:
                    self._send_json(404, {"error": "API endpoint not found."})
                    return

                save_data(students, courses, marks)
            self._send_json(201, created)
        except (ApiError, ValueError, OSError) as error:
            self._api_error(error)

    def do_DELETE(self):
        parts = [unquote(part) for part in urlsplit(self.path).path.strip("/").split("/")]
        try:
            with DATA_LOCK:
                students, courses, marks = load_data()

                if len(parts) == 3 and parts[:2] == ["api", "students"]:
                    student_id = parts[2]
                    kept_students = [
                        student for student in students if student.student_id != student_id
                    ]
                    if len(kept_students) == len(students):
                        raise ApiError(404, "Student not found.")
                    students = kept_students
                    marks = [mark for mark in marks if mark.student_id != student_id]
                elif len(parts) == 3 and parts[:2] == ["api", "courses"]:
                    course_id = parts[2]
                    kept_courses = [
                        course for course in courses if course.course_id != course_id
                    ]
                    if len(kept_courses) == len(courses):
                        raise ApiError(404, "Course not found.")
                    courses = kept_courses
                    marks = [mark for mark in marks if mark.course_id != course_id]
                elif len(parts) == 4 and parts[:2] == ["api", "marks"]:
                    student_id, course_id = parts[2:]
                    kept_marks = [
                        mark
                        for mark in marks
                        if not (
                            mark.student_id == student_id
                            and mark.course_id == course_id
                        )
                    ]
                    if len(kept_marks) == len(marks):
                        raise ApiError(404, "Mark not found.")
                    marks = kept_marks
                elif len(parts) == 3 and parts[:2] == ["api", "collections"]:
                    collection = parts[2]
                    if collection == "students":
                        students = []
                        marks = []
                    elif collection == "courses":
                        courses = []
                        marks = []
                    elif collection == "marks":
                        marks = []
                    else:
                        raise ApiError(404, "List not found.")
                else:
                    raise ApiError(404, "API endpoint not found.")

                save_data(students, courses, marks)
            self._send_json(200, {"ok": True})
        except (ApiError, OSError) as error:
            self._api_error(error)


def create_server(host="127.0.0.1", port=8000):
    return ThreadingHTTPServer((host, port), StudentAppHandler)


def run_server(host="127.0.0.1", port=8000):
    server = create_server(host, port)
    print(f"Student Desk is running at http://{host}:{server.server_port}")
    print("Press Ctrl+C to stop the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Student Desk.")
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()