import sqlite3
from pathlib import Path

# This script creates a base SQLite3 database for development purposes
# Run this script from the 'backend' folder using the command: python scripts/db_init.py
# This will place the library.db file in the correct location
# NOTE: Once you've run this script, you'll likely want to use the /register/ endpoint to insert a user into the database.

def main():
    try:
        # Connect to the database (this will create it if it doesn't exist)
        # Use pathlib to ensure the database is created in the backend directory
        backend_dir = Path(__file__).parent.parent
        db_path = backend_dir / 'library.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')

        # Create refresh_tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                jti TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                expires_at INTEGER NOT NULL,
                revoked INTEGER DEFAULT 0
            )
        ''')

        # Create books table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT,
                file_type TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # Commit changes and close connection
        conn.commit()
        conn.close()

        print("Database 'library.db' created successfully with required tables.")
        
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")
        if 'conn' in locals():
            conn.close()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    main()