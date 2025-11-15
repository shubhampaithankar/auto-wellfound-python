import aiosqlite
from typing import Optional

DB_NAME = "wellfound.db"

async def get_sqlite_connection(db_path: str = DB_NAME) -> Optional[aiosqlite.Connection]:
    """Create and return a SQLite database connection."""
    try:
        conn = await aiosqlite.connect(db_path)
        print(f"Connected to SQLite database: {db_path}")
        return conn
    except Exception as e:
        print("Error connecting to database")
        print(e)
        return None

async def init_database(conn: aiosqlite.Connection):
    """Initialize the database with the job_applications table if it doesn't exist."""
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS job_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                position TEXT NOT NULL,
                remote_policy TEXT,
                compensation TEXT,
                skills TEXT,
                description TEXT,
                status TEXT NOT NULL CHECK(status IN ('applied', 'rejected')),
                notes TEXT,
                url TEXT,
                type TEXT,
                location TEXT,
                exp_required TEXT,
                application_date TEXT,
                time TEXT
            )
        """)
        await conn.commit()
        print("Database table initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise e

