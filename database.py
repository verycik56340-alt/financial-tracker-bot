import os
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent


def get_db_path() -> Path:
    """
    Database file path: the DB_PATH environment variable if set,
    otherwise finance.db next to this file.
    """
    env_path = os.environ.get("DB_PATH")
    return Path(env_path) if env_path else _BASE_DIR / "finance.db"


def init_db():
    """
    Prepares the database: creates the table if missing
    and adds the type column if it does not exist yet (migration).
    Called once when the bot starts.
    """
    with closing(sqlite3.connect(get_db_path())) as conn:
        cursor = conn.cursor()

        # 1) Create the table if it does not exist at all.
        #    New installs get the type column right away.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                category TEXT,
                date TEXT,
                type TEXT DEFAULT 'expense'
            )
        ''')

        # 2) Migration for old databases that lack the type column.
        #    PRAGMA table_info returns the list of table columns.
        #    If 'type' is not among them, add it.
        cursor.execute("PRAGMA table_info(expenses)")
        columns = [row[1] for row in cursor.fetchall()]  # row[1] is the column name
        if "type" not in columns:
            cursor.execute("ALTER TABLE expenses ADD COLUMN type TEXT DEFAULT 'expense'")

        # 3) Set 'expense' for old rows (where type = NULL).
        cursor.execute("UPDATE expenses SET type = 'expense' WHERE type IS NULL")

        conn.commit()


def add_operation(user_id: int, amount: float, category: str,
                  date_str: str, op_type: str):
    """
    Universal operation recorder.
    op_type is 'expense' for an expense, 'income' for income.
    The function used to be called add_expense; now it handles operations in general.
    """
    with closing(sqlite3.connect(get_db_path())) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO expenses (user_id, amount, category, date, type)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, amount, category, date_str, op_type)
        )
        conn.commit()


def add_expense(user_id: int, amount: float, category: str, date_str: str):
    """
    Wrapper around add_operation: records an expense.
    The expense handlers call exactly this one - it reads more clearly.
    """
    add_operation(user_id, amount, category, date_str, "expense")


def add_income(user_id: int, amount: float, category: str, date_str: str):
    """
    Wrapper around add_operation: records income.
    """
    add_operation(user_id, amount, category, date_str, "income")


def get_monthly_operations(user_id: int, op_type: str = None):
    """
    Returns the user's operations for the current month.
    op_type: 'expense' | 'income' | None (no filter).
    Returns tuples (amount, category, date, type).
    """
    # Use the 'YYYY-MM' format to capture the whole current month
    current_month = datetime.now().strftime('%Y-%m')

    query = """
            SELECT amount, category, date, type
            FROM expenses
            WHERE user_id = ? AND date LIKE ? 
            """
    # Find all records whose date starts with the current year and month (e.g. '2026-10%')
    params = [user_id, f"{current_month}%"]

    if op_type is not None:
        query += " AND type = ?"
        params.append(op_type)

    with closing(sqlite3.connect(get_db_path())) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

def get_monthly_expenses(user_id: int):
    return get_monthly_operations(user_id, op_type='expense')

def get_monthly_incomes(user_id: int):
    return get_monthly_operations(user_id, op_type='income')