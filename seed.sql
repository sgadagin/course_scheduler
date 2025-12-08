-- seed.sql --
-- This file populates the core tables.
-- The schedules table is populated by the init_db.py script.

-- Use INSERT OR IGNORE to prevent errors if the data already exists.
-- The init_db.py script will handle deleting the old DB for a fresh start.

INSERT OR IGNORE INTO instructors (instructor_id, name, department) VALUES
  (1, 'Dr. Smith', 'Computer Science'),
  (2, 'Dr. Jones', 'Mathematics'),
  (3, 'Dr. Allen', 'Physics'),
  (4, 'Dr. King', 'Computer Science'),
  (5, 'Dr. Davis', 'History');

INSERT OR IGNORE INTO courses (course_id, title, instructor_id) VALUES
  (1, 'Introduction to Databases', 1),
  (2, 'Calculus I', 2),
  (3, 'General Physics', 3),
  (4, 'Data Structures', 1),
  (5, 'Algorithms', 4),
  (6, 'World History', 5);

INSERT OR IGNORE INTO students (student_id, name, major) VALUES
  (1, 'Alice', 'Computer Science'),
  (2, 'Bob', 'Mathematics'),
  (3, 'Charlie', 'Physics'),
  (4, 'Diana', 'Computer Science'),
  (5, 'Eve', 'History');
