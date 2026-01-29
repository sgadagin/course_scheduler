# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

DB_PATH = "scheduler.db"

# --- Database Helper ---
def get_db():
    # this method connects to an sqlite database
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.row_factory = sqlite3.Row
    return conn

# --- Flask App ---
#comment just for fun !!!
#this should cause merge conflicts later on
app.secret_key = "a_very_secret_key"
#random comment

# --- Main Route ---
@app.route("/")
def index():
    return redirect(url_for('list_schedules'))

# --- Helper Functions for Find-or-Create ---
def find_or_create_student(conn, student_name):
    """Finds a student by name. If not found, creates a new one."""
    cursor = conn.cursor()
    cursor.execute("SELECT student_id FROM students WHERE lower(name) = lower(?)", (student_name,))
    row = cursor.fetchone()
    if row:
        return row['student_id']
    else:
        cursor.execute("INSERT INTO students (name, major) VALUES (?, ?)", (student_name, 'Undeclared'))
        flash(f"New student '{student_name}' was automatically created.")
        return cursor.lastrowid

def find_or_create_instructor(conn, instructor_name):
    """Finds an instructor by name. If not found, creates a new one."""
    cursor = conn.cursor()
    cursor.execute("SELECT instructor_id FROM instructors WHERE lower(name) = lower(?)", (instructor_name,))
    row = cursor.fetchone()
    if row:
        return row['instructor_id']
    else:
        # Create a new instructor with a default department
        cursor.execute("INSERT INTO instructors (name, department) VALUES (?, ?)", (instructor_name, 'General'))
        flash(f"New instructor '{instructor_name}' was automatically created.")
        return cursor.lastrowid

# --- CRUD Routes ---
@app.route("/schedules")
def list_schedules():
    conn = get_db()
    schedules = conn.execute("""
        SELECT s.schedule_id, st.name as student_name, c.title as course_title, i.name as instructor_name, s.semester
        FROM schedules s
        JOIN students st ON s.student_id = st.student_id
        JOIN courses c ON s.course_id = c.course_id
        LEFT JOIN instructors i ON c.instructor_id = i.instructor_id
        ORDER BY st.name, s.semester
    """).fetchall()
    return render_template("schedules.html", schedules=schedules)

@app.route("/schedules/new", methods=["GET", "POST"])
def create_schedule():
    conn = get_db()
    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip()
        course_id = request.form.get("course_id")
        instructor_name = request.form.get("instructor_name", "").strip()
        semester = request.form.get("semester")

        if not all([student_name, course_id, instructor_name, semester]):
            flash("All fields are required.")
            return redirect(request.url)

        # Find or create the student and instructor
        student_id = find_or_create_student(conn, student_name)
        instructor_id = find_or_create_instructor(conn, instructor_name)

        # IMPORTANT: Update the course to use this instructor
        conn.execute("UPDATE courses SET instructor_id = ? WHERE course_id = ?", (instructor_id, course_id))

        # Finally, create the schedule entry
        conn.execute("INSERT INTO schedules (student_id, course_id, semester) VALUES (?, ?, ?)", (student_id, course_id, semester))
        conn.commit()
        flash(f"Course scheduled successfully for {student_name}.")
        return redirect(url_for('list_schedules'))

    # For the GET request, fetch all data needed for the form
    students = conn.execute("SELECT name FROM students ORDER BY name").fetchall()
    courses = conn.execute("SELECT course_id, title FROM courses ORDER BY title").fetchall()
    instructors = conn.execute("SELECT name FROM instructors ORDER BY name").fetchall()
    return render_template("schedule_form.html", students=students, courses=courses, instructors=instructors, action="Create")

@app.route("/schedules/<int:schedule_id>/edit", methods=["GET", "POST"])
def edit_schedule(schedule_id):
    conn = get_db()
    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip()
        course_id = request.form.get("course_id")
        instructor_name = request.form.get("instructor_name", "").strip()
        semester = request.form.get("semester")

        if not all([student_name, course_id, instructor_name, semester]):
            flash("All fields are required.")
            return redirect(request.url)

        student_id = find_or_create_student(conn, student_name)
        instructor_id = find_or_create_instructor(conn, instructor_name)

        # Update the course to use this instructor
        conn.execute("UPDATE courses SET instructor_id = ? WHERE course_id = ?", (instructor_id, course_id))

        # Update the schedule entry
        conn.execute("UPDATE schedules SET student_id=?, course_id=?, semester=? WHERE schedule_id=?", (student_id, course_id, semester, schedule_id))
        conn.commit()
        flash("Schedule updated successfully.")
        return redirect(url_for('list_schedules'))

    # For the GET request, fetch existing data for the form
    schedule = conn.execute("""
        SELECT s.*, st.name as student_name, i.name as instructor_name
        FROM schedules s
        JOIN students st ON s.student_id = st.student_id
        JOIN courses c ON s.course_id = c.course_id
        LEFT JOIN instructors i ON c.instructor_id = i.instructor_id
        WHERE s.schedule_id = ?
    """, (schedule_id,)).fetchone()
    students = conn.execute("SELECT name FROM students ORDER BY name").fetchall()
    courses = conn.execute("SELECT course_id, title FROM courses ORDER BY title").fetchall()
    instructors = conn.execute("SELECT name FROM instructors ORDER BY name").fetchall()
    return render_template("schedule_form.html", schedule=schedule, students=students, courses=courses, instructors=instructors, action="Update")

@app.route("/schedules/<int:schedule_id>/delete", methods=["POST"])
def delete_schedule(schedule_id):
    conn = get_db()
    conn.execute("DELETE FROM schedules WHERE schedule_id = ?", (schedule_id,))
    conn.commit()
    flash("Scheduled course dropped.")
    return redirect(url_for('list_schedules'))

@app.route("/report", methods=["GET"])
def report():
    conn = get_db()
    # Fetch data for all filter dropdowns
    students = conn.execute("SELECT student_id, name FROM students ORDER BY name").fetchall()
    courses = conn.execute("SELECT course_id, title FROM courses ORDER BY title").fetchall()
    # NEW: Fetch instructors for the new filter
    instructors = conn.execute("SELECT instructor_id, name FROM instructors ORDER BY name").fetchall()

    # Get filter values from URL query
    filters = {
        "student_id": request.args.get("student_id", type=int),
        "course_id": request.args.get("course_id", type=int),
        # NEW: Get instructor_id from the form
        "instructor_id": request.args.get("instructor_id", type=int),
        "semester": request.args.get("semester")
    }

    # Build the query dynamically
    sql = """
        SELECT st.name as student_name, c.title as course_title, i.name as instructor_name, s.semester
        FROM schedules s
        JOIN students st ON s.student_id = st.student_id
        JOIN courses c ON s.course_id = c.course_id
        LEFT JOIN instructors i ON c.instructor_id = i.instructor_id
        WHERE 1=1
    """
    params = []
    if filters["student_id"]:
        sql += " AND s.student_id = ?"
        params.append(filters["student_id"])
    if filters["course_id"]:
        sql += " AND s.course_id = ?"
        params.append(filters["course_id"])
    # NEW: Add the instructor filter to the SQL query
    if filters["instructor_id"]:
        sql += " AND c.instructor_id = ?"
        params.append(filters["instructor_id"])
    if filters["semester"]:
        sql += " AND s.semester = ?"
        params.append(filters["semester"])

    sql += " ORDER BY st.name, s.semester"
    report_rows = conn.execute(sql, params).fetchall()

    # Pass the new instructors list to the template
    return render_template(
        "report.html",
        students=students,
        courses=courses,
        instructors=instructors, # NEW
        rows=report_rows,
        filters=filters
    )
if __name__ == "__main__":
    app.run(debug=True)
