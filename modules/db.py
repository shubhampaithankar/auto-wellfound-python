import aiosqlite
from typing import Optional, Dict, Any

DB_NAME = "wellfound.db"

# Global connection variable
_db_conn: Optional[aiosqlite.Connection] = None

async def get_sqlite_connection(db_path: str = DB_NAME) -> Optional[aiosqlite.Connection]:
    """Create and return a SQLite database connection. Reuses existing connection if available."""
    global _db_conn
    if _db_conn is not None:
        return _db_conn
    
    try:
        conn = await aiosqlite.connect(db_path)
        print(f"Connected to SQLite database: {db_path}")
        _db_conn = conn
        return conn
    except Exception as e:
        print("Error connecting to database")
        print(e)
        return None

async def close_connection():
    """Close the database connection."""
    global _db_conn
    if _db_conn is not None:
        await _db_conn.close()
        _db_conn = None

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

async def store_single_job(job_obj: Dict[str, Any], status: str) -> bool:
    """Store a single job immediately in the database.
    
    Args:
        job_obj: Dictionary containing job data
        status: Either 'applied' or 'rejected'
    
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = await get_sqlite_connection()
        if not conn:
            print("Failed to get database connection for storing job")
            return False
        
        # Ensure database is initialized
        await init_database(conn)
        
        # Prepare query for inserting job
        query = """
            INSERT INTO job_applications 
            (company_name, position, remote_policy, compensation, skills, description, status, notes, url, type, location, exp_required, application_date, time) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        data = (
            job_obj.get('company_name', 'Unknown Company'),
            job_obj.get('position', 'Unknown Position'),
            job_obj.get('remote_policy', None),
            job_obj.get('compensation', None),
            job_obj.get('skills', None),
            job_obj.get('description', None),
            status,
            job_obj.get('notes', None),
            job_obj.get('url', None),
            job_obj.get('type', None),
            job_obj.get('location', None),
            job_obj.get('exp_required', None),
            job_obj.get('application_date', None),
            job_obj.get('time', None),
        )
        
        await conn.execute(query, data)
        await conn.commit()
        return True
        
    except Exception as e:
        print(f"Error storing job in database: {e}")
        return False

