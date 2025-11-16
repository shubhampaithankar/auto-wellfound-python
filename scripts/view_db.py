"""
Simple script to view the contents of the wellfound.db database.
Run this script to see all stored job applications.
"""
import asyncio
import aiosqlite
from services.db import DB_NAME

async def view_database():
    """View all jobs in the database."""
    try:
        conn = await aiosqlite.connect(DB_NAME)
        cursor = await conn.cursor()
        
        # Get total counts
        await cursor.execute("SELECT COUNT(*) FROM job_applications WHERE status = 'applied'")
        applied_count = await cursor.fetchone()
        
        await cursor.execute("SELECT COUNT(*) FROM job_applications WHERE status = 'rejected'")
        rejected_count = await cursor.fetchone()
        
        print("=" * 80)
        print(f"Database: {DB_NAME}")
        print(f"Total Applied: {applied_count[0]}")
        print(f"Total Rejected: {rejected_count[0]}")
        print("=" * 80)
        print()
        
        # Show all jobs
        await cursor.execute("""
            SELECT 
                id, company_name, position, status, 
                remote_policy, compensation, type, location,
                exp_required, application_date, time, notes
            FROM job_applications 
            ORDER BY id DESC
            LIMIT 50
        """)
        
        rows = await cursor.fetchall()
        
        if not rows:
            print("No jobs found in database.")
            return
        
        print(f"Showing last {len(rows)} jobs:\n")
        
        for row in rows:
            id, company, position, status, remote, comp, job_type, location, exp, app_date, time, notes = row
            
            print(f"[{id}] {status.upper()}")
            print(f"  Company: {company}")
            print(f"  Position: {position}")
            if remote:
                print(f"  Remote Policy: {remote}")
            if location:
                print(f"  Location: {location}")
            if job_type:
                print(f"  Type: {job_type}")
            if comp:
                print(f"  Compensation: {comp}")
            if exp:
                print(f"  Experience Required: {exp}")
            if app_date:
                print(f"  Application Date: {app_date}")
            if time:
                print(f"  Processed: {time}")
            if notes:
                print(f"  Notes: {notes}")
            print("-" * 80)
        
        await cursor.close()
        await conn.close()
        
    except FileNotFoundError:
        print(f"Database file '{DB_NAME}' not found. Run the main script first to create it.")
    except Exception as e:
        print(f"Error viewing database: {e}")

if __name__ == "__main__":
    asyncio.run(view_database())

