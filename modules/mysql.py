import aiomysql
from aiomysql.pool import Pool
from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

DB_NAME = "wellfound"

async def get_mysql_connection(host: str, port: int, user: str, password: str):
  try:
    pool: Pool = await aiomysql.create_pool(host=host, port=port, user=user, password=password)
    print(f"Connected to MySQL successfully")
    connection: Connection = await pool.acquire()
    cursor: Cursor = await connection.cursor()
    return cursor    
  except Exception as e: 
    print("Error connecting to database")
    print(e)
    return None
