-- schema.sql
PRAGMA foreign_keys = ON; -- Enforce foreign key constraints in SQLite

CREATE TABLE IF NOT EXISTS instructors (
  instructor_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  department TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
  course_id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  instructor_id INTEGER,
  FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id)
);

CREATE TABLE IF NOT EXISTS students (
  student_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  major TEXT NOT NULL
);

-- Main table for CRUD operations (Requirement 1)
CREATE TABLE IF NOT EXISTS schedules (
  schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  course_id INTEGER NOT NULL,
  semester TEXT NOT NULL, -- e.g., "Fall 2025"
  FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
  FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_schedules_student_semester ON schedules (student_id, semester);
CREATE INDEX IF NOT EXISTS idx_courses_instructor ON courses (instructor_id);
CREATE INDEX IF NOT EXISTS idx_students_name ON students (name);
