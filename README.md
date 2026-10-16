USTH Advanced Programming with Python 2026
==================================

* Ha Duc Manh  
* 2510743

## Practical Work 5

### Run the student web app

From the `Python-2026-L1` directory, start the local app with:

```powershell
python -m pw5.web
```

Open the address printed in the terminal (normally `http://127.0.0.1:8000`). Press `Ctrl+C` in the terminal to stop the server.

The app lets you manage students, courses, and marks, browse credit-weighted GPA rankings, search records, and remove individual or complete lists. Records are stored as JSON in `pw5/students.txt`, `pw5/courses.txt`, and `pw5/marks.txt`. The server binds to `127.0.0.1`, so it is only available on the local computer.

### Run the terminal version

```powershell
python -m pw5.main
```

## Practical Work 8

The multithreaded version is in `pw8`. Run it from the `Python-2026-L1`
directory with either `python -m pw8.main` for the terminal application or
`python -m pw8.web` for the web application. It persists compressed pickle
snapshots on a background worker and flushes pending saves when the
application exits.