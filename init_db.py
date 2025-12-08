# init_db.py
import sqlite3
from pathlib import Path

DB_PATH = "scheduler.db"

def init_db():
    """Creates the database and seeds it with initial data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Run schema and seed SQL files to create tables and populate them
    with open("schema.sql") as f:
        conn.executescript(f.read())
    with open("seed.sql") as f:
        conn.executescript(f.read())

    # Add a variety of initial schedule entries for a richer demo
    schedules_to_add = [
        # Alice's schedule
        (1, 1, 'Fall 2025'),   # Alice in Databases
        (1, 4, 'Fall 2025'),   # Alice in Data Structures
        (1, 5, 'Spring 2026'), # Alice in Algorithms

        # Bob's schedule
        (2, 2, 'Fall 2025'),   # Bob in Calculus I

        # Charlie's schedule
        (3, 3, 'Fall 2025'),   # Charlie in General Physics

        # Diana's schedule
        (4, 1, 'Fall 2025'),   # Diana in Databases
        (4, 5, 'Spring 2026'), # Diana in Algorithms

        # Eve's schedule
        (5, 6, 'Fall 2025')    # Eve in World History
    ]

    # Use executemany to insert all the schedule records
    cursor.executemany(
        "INSERT OR IGNORE INTO schedules (student_id, course_id, semester) VALUES (?, ?, ?);",
        schedules_to_add
    )

    conn.commit()
    conn.close()
    print("Database has been initialized with expanded data.")


if __name__ == "__main__":
    # Check if the database file already exists.
    if Path(DB_PATH).exists():
        print(f"Database '{DB_PATH}' already exists.")
        # Ask the user for confirmation before deleting it
        user_input = input("Do you want to delete it and re-initialize with new data? (yes/no): ")
        if user_input.lower() == 'yes':
            Path(DB_PATH).unlink() # Delete the file
            print("Old database deleted.")
            init_db() # Create and seed the new one
        else:
            print("Initialization cancelled.")
    else:
        # If the database doesn't exist, just create it
        init_db()
