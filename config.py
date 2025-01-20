
import os
import sqlite3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database setup (SQLite)
DATABASE_PATH = os.getenv("DATABASE_PATH", "app.db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#OPENAI_API_KEY ="sk-svcacct-lcLnrJvrM9V6Td__hB2sXQoJsxdJIXrPfJpfxDTqZolXzbdVXWJg6eYiQtEChT3BlbkFJjdXc2OWPAqDjAZ64-UAjeAmWSRbvhRP8aiQn04dID4WDdz8cu0zOHfSTw0rggA"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn
