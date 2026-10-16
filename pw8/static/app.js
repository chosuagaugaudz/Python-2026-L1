const savedGpaScale = Number(localStorage.getItem("studentDeskGpaScale"));

const state = {
  data: { students: [], courses: [], marks: [] },
  view: "overview",
  studentQuery: "",
  markCourse: "",
  gpaScale: [4, 10, 20].includes(savedGpaScale) ? savedGpaScale : 10,
};

const viewNames = {
  overview: "HOME",
  students: "STUDENTS",
  courses: "COURSES",
  marks: "MARKS",
  gpa: "GPA RANKING",
};

const api = async (path, options = {}) => {
  const response = await fetch(path, {
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.error || "The request could not be completed.");
  return body;
};

function escapeHTML(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[character]);
}

function showToast(message, isError = false) {
  const toast = document.createElement("div");
  toast.className = `toast${isError ? " error" : ""}`;
  toast.textContent = message;
  document.querySelector("#toast-region").append(toast);
  window.setTimeout(() => toast.remove(), 3600);
}

function setConnection(connected) {
  const dot = document.querySelector("#connection-dot");
  dot.classList.toggle("online", connected);
  dot.classList.toggle("offline", !connected);
  document.querySelector("#connection-label").textContent = connected ? "Saved locally" : "Offline";
}

function gpaFor(student) {
  let weightedTotal = 0;
  let creditTotal = 0;
  for (const mark of state.data.marks) {
    if (mark.student_id !== student.student_id) continue;
    const course = state.data.courses.find((item) => item.course_id === mark.course_id);
    if (!course) continue;
    weightedTotal += (mark.value / (mark.scale || 10) * 10) * course.credits;
    creditTotal += course.credits;
  }
  return creditTotal ? weightedTotal / creditTotal : null;
}

function displayedAverage(average) {
  if (average === null) return null;
  const scaledAverage = average / 10 * state.gpaScale;
  return state.gpaScale === 4 ? scaledAverage.toFixed(2) : scaledAverage.toFixed(1);
}

function averageHeading() {
  return "AVERAGE / 20";
}

function gpaHeading() {
  return state.gpaScale === 4 ? "GPA / 4.0" : `AVERAGE / ${state.gpaScale}`;
}

function averageOutOf20(average) {
  return average === null ? null : (average * 2).toFixed(1);
}

function formatDate(value) {
  if (!value) return "—";
  const date = String(value);
  const isoMatch = date.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (isoMatch) return `${isoMatch[3]}/${isoMatch[2]}/${isoMatch[1]}`;
  const dayFirstMatch = date.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
  return dayFirstMatch ? date : escapeHTML(date);
}

function personCell(student, caption = student.student_id) {
  const initial = escapeHTML((student.name || "?").trim().charAt(0).toUpperCase());
  return `<div class="person-cell"><span class="person-monogram">${initial}</span><span><span class="person-name">${escapeHTML(student.name)}</span><span class="person-caption">${escapeHTML(caption)}</span></span></div>`;
}

function emptyState(title, message) {
  return `<div class="empty-state"><span class="empty-symbol" aria-hidden="true">+</span><strong>${escapeHTML(title)}</strong><span>${escapeHTML(message)}</span></div>`;
}

function table(headers, rows, className = "") {
  if (!rows.length) return emptyState("Nothing here yet", "Add a record to see it appear in this list.");
  return `<table class="data-table ${className}"><thead><tr>${headers.map((header) => `<th>${header}</th>`).join("")}</tr></thead><tbody>${rows.join("")}</tbody></table>`;
}

function renderOverview() {
  const { students, courses, marks } = state.data;
  const averages = students.map(gpaFor).filter((value) => value !== null);
  const classAverage = averages.length ? averages.reduce((sum, value) => sum + value, 0) / averages.length : null;
  document.querySelector("#student-count").textContent = students.length;
  document.querySelector("#course-count").textContent = courses.length;
  document.querySelector("#mark-count").textContent = marks.length;
  document.querySelector("#average-gpa").textContent = averageOutOf20(classAverage) ?? "—";
  const recent = [...students].slice(-5).reverse();
  const rows = recent.map((student) => `<tr><td>${personCell(student)}</td><td>${formatDate(student.dob)}</td><td>${averageOutOf20(gpaFor(student)) ?? '<span class="no-grade">No marks</span>'}</td></tr>`);
  document.querySelector("#recent-students").innerHTML = students.length
    ? table(["STUDENT", "DATE OF BIRTH", averageHeading()], rows)
    : emptyState("Your register starts here", "Add a student to begin building the roster.");
}

function renderStudents() {
  const query = state.studentQuery.trim().toLowerCase();
  const alphabetized = [...state.data.students].sort((left, right) =>
    left.name.localeCompare(right.name, undefined, { sensitivity: "base" })
    || left.student_id.localeCompare(right.student_id),
  );
  const filtered = alphabetized
    .map((student, index) => ({ student, rosterNumber: index + 1 }))
    .filter(({ student }) => `${student.name} ${student.student_id}`.toLowerCase().includes(query));
  document.querySelector("#student-results-count").textContent = `${filtered.length} ${filtered.length === 1 ? "STUDENT" : "STUDENTS"}`;
  const rows = filtered.map(({ student, rosterNumber }) => {
    const average = gpaFor(student);
    return `<tr><td class="roster-number">${String(rosterNumber).padStart(2, "0")}</td><td>${personCell(student)}</td><td>${escapeHTML(student.student_id)}</td><td>${formatDate(student.dob)}</td><td>${averageOutOf20(average) ?? '<span class="no-grade">No marks</span>'}</td><td class="action-cell"><button class="row-delete" data-remove="students" data-id="${escapeHTML(student.student_id)}" data-label="${escapeHTML(student.name)}" title="Remove student" aria-label="Remove ${escapeHTML(student.name)}">×</button></td></tr>`;
  });
  document.querySelector("#students-table").innerHTML = filtered.length
    ? table(["NO.", "STUDENT", "ID", "DATE OF BIRTH", averageHeading(), ""], rows)
    : emptyState(query ? "No matching students" : "No students yet", query ? "Try a different name or student ID." : "Add a student to create your first record.");
}

function renderCourses() {
  const rows = state.data.courses.map((course) => {
    const markCount = state.data.marks.filter((mark) => mark.course_id === course.course_id).length;
    return `<tr><td><span class="person-name">${escapeHTML(course.name)}</span></td><td class="table-id">${escapeHTML(course.course_id)}</td><td><span class="course-chip">${escapeHTML(course.credits)}</span></td><td>${markCount}</td><td class="action-cell"><button class="row-delete" data-remove="courses" data-id="${escapeHTML(course.course_id)}" data-label="${escapeHTML(course.name)}" title="Remove course" aria-label="Remove ${escapeHTML(course.name)}">×</button></td></tr>`;
  });
  document.querySelector("#course-results-count").textContent = `${state.data.courses.length} ${state.data.courses.length === 1 ? "COURSE" : "COURSES"}`;
  document.querySelector("#courses-table").innerHTML = table(["COURSE", "COURSE ID", "CREDITS", "MARKS", ""], rows);
}

function renderMarkFilter() {
  const select = document.querySelector("#mark-course-filter");
  const selected = state.markCourse;
  select.innerHTML = `<option value="">All courses</option>${state.data.courses.map((course) => `<option value="${escapeHTML(course.course_id)}">${escapeHTML(course.name)}</option>`).join("")}`;
  if (state.data.courses.some((course) => course.course_id === selected)) select.value = selected;
  else state.markCourse = "";
}

function renderMarks() {
  renderMarkFilter();
  const students = new Map(state.data.students.map((student) => [student.student_id, student]));
  const courses = new Map(state.data.courses.map((course) => [course.course_id, course]));
  const filtered = state.data.marks.filter((mark) => !state.markCourse || mark.course_id === state.markCourse);
  const rows = filtered.map((mark) => {
    const student = students.get(mark.student_id) || { student_id: mark.student_id, name: "Unknown student" };
    const course = courses.get(mark.course_id) || { course_id: mark.course_id, name: "Unknown course" };
    const scale = mark.scale || 20;
    const normalizedValue = mark.value / scale * 20;
    const gradeClass = normalizedValue < 5 ? " grade-low" : normalizedValue < 7 ? " grade-mid" : "";
    const scoreOutOf20 = normalizedValue.toFixed(1);
    const scaledGradeClass = normalizedValue < 10 ? " grade-low" : normalizedValue < 14 ? " grade-mid" : "";
    return `<tr><td>${personCell(student)}</td><td><span class="person-name">${escapeHTML(course.name)}</span><span class="person-caption">${escapeHTML(course.course_id)}</span></td><td><span class="grade-value${scaledGradeClass || gradeClass}">${scoreOutOf20}/20</span></td><td class="action-cell"><button class="row-delete" data-remove="marks" data-student="${escapeHTML(mark.student_id)}" data-course="${escapeHTML(mark.course_id)}" data-label="${escapeHTML(student.name)} / ${escapeHTML(course.name)}" title="Remove mark" aria-label="Remove mark for ${escapeHTML(student.name)}">×</button></td></tr>`;
  });
  document.querySelector("#mark-results-count").textContent = `${filtered.length} ${filtered.length === 1 ? "MARK" : "MARKS"}`;
  document.querySelector("#marks-table").innerHTML = table(["STUDENT", "COURSE", "RESULT", ""], rows);
}

function renderGpa() {
  const ranked = state.data.students.map((student) => ({ student, average: gpaFor(student) }));
  ranked.sort((left, right) => {
    if (left.average === null) return right.average === null ? left.student.name.localeCompare(right.student.name) : 1;
    if (right.average === null) return -1;
    return right.average - left.average || left.student.name.localeCompare(right.student.name);
  });
  const rows = ranked.map(({ student, average }, index) => {
    const width = average === null ? 0 : Math.max(0, Math.min(100, average * 10));
    return `<tr class="${index === 0 && average !== null ? "rank-leading" : ""}"><td class="rank-number">${String(index + 1).padStart(2, "0")}</td><td>${personCell(student)}</td><td class="rank-bar-cell"><div class="rank-track"><span style="width:${width}%"></span></div></td><td class="rank-score">${displayedAverage(average) ?? '<span class="no-grade">—</span>'}</td><td class="action-cell"><button class="row-delete" data-remove="students" data-id="${escapeHTML(student.student_id)}" data-label="${escapeHTML(student.name)}" title="Remove student" aria-label="Remove ${escapeHTML(student.name)}">×</button></td></tr>`;
  });
  document.querySelector("#gpa-table").innerHTML = table(["RANK", "STUDENT", "RELATIVE SCORE", gpaHeading(), ""], rows);
}

function render() {
  for (const page of document.querySelectorAll(".page")) page.hidden = page.id !== `page-${state.view}`;
  for (const link of document.querySelectorAll(".nav-link")) link.classList.toggle("active", link.dataset.view === state.view);
  document.querySelector("#current-section").textContent = viewNames[state.view];
  document.querySelector("#gpa-scale").value = String(state.gpaScale);
  renderOverview();
  renderStudents();
  renderCourses();
  renderMarks();
  renderGpa();
}

async function refresh() {
  try {
    state.data = await api("/api/data");
    setConnection(true);
    render();
  } catch (error) {
    setConnection(false);
    showToast(error.message, true);
  }
}

function setView(view) {
  if (!viewNames[view]) return;
  state.view = view;
  render();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

const dialog = document.querySelector("#record-dialog");
const recordForm = document.querySelector("#record-form");
const importDialog = document.querySelector("#import-dialog");
const importForm = document.querySelector("#import-form");
let currentRecordType = "student";
let importContent = "";
let importPreview = null;

function field(label, name, type = "text", attributes = "") {
  return `<label class="form-field">${label}<input name="${name}" type="${type}" ${attributes} required></label>`;
}

function selectField(label, name, options) {
  return `<label class="form-field">${label}<select name="${name}" required><option value="" disabled selected>Choose ${label.toLowerCase()}</option>${options.map((option) => `<option value="${escapeHTML(option.value)}">${escapeHTML(option.label)}</option>`).join("")}</select></label>`;
}

function openDialog(type) {
  if (type === "mark" && (!state.data.students.length || !state.data.courses.length)) {
    showToast("Add at least one student and one course before recording marks.", true);
    return;
  }
  currentRecordType = type;
  const titles = { student: "Add student", course: "Add course", mark: "Record a mark" };
  const dateOfBirthField = '<div class="dob-row"><label class="form-field">Date of birth<input name="record_birth_date" type="text" inputmode="numeric" placeholder="DD/MM/YYYY" maxlength="10" autocomplete="off" required><span class="field-hint">Day / month / year</span></label><button class="field-undo" type="button" id="dob-undo" disabled>Undo date</button></div>';
  const fields = {
    student: field("Student ID", "record_student_code", "text", 'placeholder="e.g. STU-024" autocomplete="off"') + field("Full name", "record_student_name", "text", 'placeholder="Student name" autocomplete="off"') + dateOfBirthField,
    course: field("Course ID", "course_id", "text", 'placeholder="e.g. CS204" autocomplete="off"') + field("Course name", "name", "text", 'placeholder="Course title"') + field("Credits", "credits", "number", 'min="1" step="1" placeholder="3"'),
    mark: selectField("Student", "student_id", state.data.students.map((student) => ({ value: student.student_id, label: `${student.name} · ${student.student_id}` }))) + selectField("Course", "course_id", state.data.courses.map((course) => ({ value: course.course_id, label: `${course.name} · ${course.course_id}` }))) + field("Mark out of 20", "value", "number", 'min="0" max="20" step="0.1" placeholder="0 to 20"'),
  };
  document.querySelector("#dialog-title").textContent = titles[type];
  document.querySelector("#dialog-eyebrow").textContent = type === "mark" ? "ASSESSMENT" : "NEW RECORD";
  document.querySelector("#form-fields").innerHTML = fields[type];
  const dobInput = document.querySelector("#form-fields [name='record_birth_date']");
  if (dobInput) {
    const previousDate = dobInput.value;
    const undoButton = document.querySelector("#dob-undo");
    const restoreDate = () => {
      dobInput.value = previousDate;
      undoButton.disabled = true;
    };
    const formatDateInput = () => {
      const caret = dobInput.selectionStart ?? dobInput.value.length;
      const digitsBeforeCaret = dobInput.value.slice(0, caret).replace(/\D/g, "").length;
      const digits = dobInput.value.replace(/\D/g, "").slice(0, 8);
      const day = digits.slice(0, 2);
      const month = digits.slice(2, 4);
      const year = digits.slice(4, 8);
      dobInput.value = day + (digits.length > 2 ? `/${month}` : "") + (digits.length > 4 ? `/${year}` : "");
      const separatorCount = Number(digitsBeforeCaret > 2) + Number(digitsBeforeCaret > 4);
      const nextCaret = Math.min(dobInput.value.length, digitsBeforeCaret + separatorCount);
      dobInput.setSelectionRange(nextCaret, nextCaret);
      updateUndoButton();
    };
    const updateUndoButton = () => {
      undoButton.disabled = dobInput.value === previousDate;
    };
    dobInput.addEventListener("input", formatDateInput);
    dobInput.addEventListener("change", updateUndoButton);
    dobInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        restoreDate();
      }
    });
    undoButton.addEventListener("click", restoreDate);
  }
  for (const input of document.querySelectorAll("#form-fields input")) {
    input.readOnly = true;
    input.autocomplete = "new-password";
    input.addEventListener("focus", () => {
      input.value = "";
      input.readOnly = false;
    }, { once: true });
  }
  document.querySelector("#form-error").textContent = "";
  dialog.showModal();
  document.querySelector("#dialog-close").focus();
}

function closeDialog() {
  dialog.close();
}

function openImportDialog() {
  importForm.reset();
  importContent = "";
  importPreview = null;
  document.querySelector("#import-preview").hidden = true;
  document.querySelector("#import-error").textContent = "";
  document.querySelector("#import-submit").disabled = true;
  document.querySelector("#import-submit").textContent = "Import students";
  importDialog.showModal();
  document.querySelector("#import-close").focus();
}

async function previewStudentFile(file) {
  importContent = "";
  importPreview = null;
  const preview = document.querySelector("#import-preview");
  const submit = document.querySelector("#import-submit");
  const error = document.querySelector("#import-error");
  preview.hidden = true;
  submit.disabled = true;
  error.textContent = "";
  if (!file) return;

  try {
    importContent = await file.text();
    importPreview = await api("/api/students/import/preview", {
      method: "POST",
      body: JSON.stringify({ content: importContent }),
    });
    const readyCount = importPreview.students.length;
    const skippedCount = importPreview.skipped.length + importPreview.errors.length;
    document.querySelector("#import-summary").textContent = `${readyCount} ready to import · ${importPreview.generated} IDs generated · ${skippedCount} rows skipped`;
    const issues = [...importPreview.skipped, ...importPreview.errors];
    document.querySelector("#import-issues").innerHTML = issues.length
      ? issues.slice(0, 5).map((issue) => `<li>${escapeHTML(issue)}</li>`).join("")
      : "";
    const rows = importPreview.students.slice(0, 5).map((student) => `<tr><td>${escapeHTML(student.name)}</td><td>${escapeHTML(student.student_id)}</td><td>${escapeHTML(student.dob || "—")}</td></tr>`);
    document.querySelector("#import-sample").innerHTML = rows.length
      ? `<table class="data-table"><thead><tr><th>NAME</th><th>STUDENT ID</th><th>DOB</th></tr></thead><tbody>${rows.join("")}</tbody></table>`
      : "";
    preview.hidden = false;
    submit.disabled = readyCount === 0;
    submit.textContent = `Import ${readyCount} student${readyCount === 1 ? "" : "s"}`;
  } catch (previewError) {
    error.textContent = previewError.message;
  }
}

async function importStudents(event) {
  event.preventDefault();
  if (!importContent || !importPreview?.students.length) return;
  const submit = document.querySelector("#import-submit");
  submit.disabled = true;
  try {
    const result = await api("/api/students/import", {
      method: "POST",
      body: JSON.stringify({ content: importContent }),
    });
    importDialog.close();
    await refresh();
    setView("students");
    const skipped = result.skipped.length + result.errors.length;
    showToast(`${result.students.length} students imported${skipped ? `; ${skipped} rows skipped` : ""}.`);
  } catch (error) {
    document.querySelector("#import-error").textContent = error.message;
    submit.disabled = false;
  }
}

function downloadStudentTemplate() {
  const file = new Blob(["student_id,name,dob\nSTU-0001,Example Student,01/01/2000\n"], { type: "text/csv" });
  const url = URL.createObjectURL(file);
  const link = document.createElement("a");
  link.href = url;
  link.download = "students-template.csv";
  link.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

async function saveRecord(event) {
  event.preventDefault();
  const formData = new FormData(recordForm);
  const payload = Object.fromEntries(formData.entries());
  if (currentRecordType === "student") {
    const dateMatch = payload.record_birth_date?.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
    const parsedDate = dateMatch && new Date(Number(dateMatch[3]), Number(dateMatch[2]) - 1, Number(dateMatch[1]));
    if (!parsedDate || parsedDate.getFullYear() !== Number(dateMatch[3]) || parsedDate.getMonth() !== Number(dateMatch[2]) - 1 || parsedDate.getDate() !== Number(dateMatch[1])) {
      document.querySelector("#form-error").textContent = "Enter a real date in DD/MM/YYYY format.";
      return;
    }
    payload.student_id = payload.record_student_code;
    payload.name = payload.record_student_name;
    payload.dob = payload.record_birth_date;
    delete payload.record_student_code;
    delete payload.record_student_name;
    delete payload.record_birth_date;
  }
  if (currentRecordType === "course") payload.credits = Number(payload.credits);
  if (currentRecordType === "mark") {
    payload.value = String(payload.value).replace(",", ".");
    payload.scale = 20;
  }
  const error = document.querySelector("#form-error");
  error.textContent = "";
  const submit = document.querySelector("#dialog-submit");
  submit.disabled = true;
  try {
    await api(`/api/${currentRecordType === "mark" ? "marks" : `${currentRecordType}s`}`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    closeDialog();
    await refresh();
    showToast(`${currentRecordType === "mark" ? "Mark" : currentRecordType[0].toUpperCase() + currentRecordType.slice(1)} saved.`);
  } catch (saveError) {
    error.textContent = saveError.message;
  } finally {
    submit.disabled = false;
  }
}

async function removeRecord(button) {
  const kind = button.dataset.remove;
  const label = button.dataset.label;
  if (!window.confirm(`Remove ${label}?${kind === "students" || kind === "courses" ? " Related marks will also be removed." : ""}`)) return;
  let path;
  if (kind === "marks") path = `/api/marks/${encodeURIComponent(button.dataset.student)}/${encodeURIComponent(button.dataset.course)}`;
  else path = `/api/${kind}/${encodeURIComponent(button.dataset.id)}`;
  try {
    await api(path, { method: "DELETE" });
    await refresh();
    showToast("Record removed.");
  } catch (error) {
    showToast(error.message, true);
  }
}

async function clearCollection(kind) {
  const labels = { students: "students and their marks", courses: "courses and their marks", marks: "marks" };
  if (!window.confirm(`Clear all ${labels[kind]}? This cannot be undone.`)) return;
  try {
    await api(`/api/collections/${kind}`, { method: "DELETE" });
    await refresh();
    showToast(`${labels[kind][0].toUpperCase()}${labels[kind].slice(1)} cleared.`);
  } catch (error) {
    showToast(error.message, true);
  }
}

document.addEventListener("click", (event) => {
  const target = event.target.closest("button");
  if (!target) return;
  if (target.matches(".nav-link")) setView(target.dataset.view);
  else if (target.dataset.go) setView(target.dataset.go);
  else if (target.dataset.import === "students") openImportDialog();
  else if (target.id === "import-students") openImportDialog();
  else if (target.dataset.add) openDialog(target.dataset.add);
  else if (target.dataset.clear) clearCollection(target.dataset.clear);
  else if (target.dataset.remove) removeRecord(target);
  else if (target.id === "import-close" || target.id === "import-cancel") importDialog.close();
  else if (target.id === "dialog-close" || target.id === "dialog-cancel") closeDialog();
});

document.querySelector(".brand").addEventListener("click", (event) => {
  event.preventDefault();
  setView("overview");
});

document.querySelector("#student-search").addEventListener("input", (event) => {
  state.studentQuery = event.target.value;
  renderStudents();
});
document.querySelector("#mark-course-filter").addEventListener("change", (event) => {
  state.markCourse = event.target.value;
  renderMarks();
});
document.querySelector("#gpa-scale").addEventListener("change", (event) => {
  state.gpaScale = Number(event.target.value);
  localStorage.setItem("studentDeskGpaScale", String(state.gpaScale));
  render();
});
document.querySelector("#import-file").addEventListener("change", (event) => {
  previewStudentFile(event.target.files[0]);
});
importForm.addEventListener("submit", importStudents);
document.querySelector("#download-student-template").addEventListener("click", downloadStudentTemplate);
recordForm.addEventListener("submit", saveRecord);
importDialog.addEventListener("click", (event) => {
  if (event.target === importDialog) importDialog.close();
});
dialog.addEventListener("click", (event) => {
  if (event.target === dialog) closeDialog();
});

document.querySelector("#today-date").textContent = new Intl.DateTimeFormat("en", {
  weekday: "short",
  day: "numeric",
  month: "long",
  year: "numeric",
}).format(new Date());
refresh();
