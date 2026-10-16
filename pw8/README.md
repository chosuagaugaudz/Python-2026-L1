# Practical Work 8

Run the terminal application from the `Python-2026-L1` directory:

```powershell
python -m pw8.main
```

Run the web application with:

```powershell
python -m pw8.web
```

The application saves snapshots of student, course, and mark data using a
single background worker. The snapshots are pickled, compressed with gzip, and
stored in `pw8/students.dat`. The terminal application waits for pending saves
when it exits, and the web server waits for its request threads and pending
saves when it shuts down. Existing gzip-compressed JSON archives and the
individual JSON text files remain readable and are migrated to the new format
on the next save.
