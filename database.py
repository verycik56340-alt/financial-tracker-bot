import sqlite3
from datetime import datetime

DB_NAME = "finance.db"


def init_db():
    """
    Готовит базу к работе: создаёт таблицу, если её нет,
    и добавляет колонку type, если её ещё нет (миграция).
    Вызывается один раз при старте бота.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        # 1) Создаём таблицу, если её вообще нет.
        #    Для новых установок сразу с колонкой type.
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

        # 2) Миграция для старых баз, где колонки type ещё нет.
        #    PRAGMA table_info возвращает список колонок таблицы.
        #    Если среди них нет 'type' — добавляем её.
        cursor.execute("PRAGMA table_info(expenses)")
        columns = [row[1] for row in cursor.fetchall()]  # row[1] — имя колонки
        if "type" not in columns:
            cursor.execute("ALTER TABLE expenses ADD COLUMN type TEXT DEFAULT 'expense'")

        # 3) Старым строкам (у которых type = NULL) проставляем 'expense'.
        cursor.execute("UPDATE expenses SET type = 'expense' WHERE type IS NULL")

        conn.commit()


def add_operation(user_id: int, amount: float, category: str,
                  date_str: str, op_type: str):
    """
    Универсальная запись операции.
    op_type — 'expense' для расхода, 'income' для дохода.
    Раньше функция называлась add_expense; теперь она про операции вообще.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO expenses (user_id, amount, category, date, type)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, amount, category, date_str, op_type)
        )
        conn.commit()


def add_expense(user_id: int, amount: float, category: str, date_str: str):
    """
    Обёртка над add_operation: пишет расход.
    Хендлеры расхода вызывают именно её — читается понятнее.
    """
    add_operation(user_id, amount, category, date_str, "expense")


def add_income(user_id: int, amount: float, category: str, date_str: str):
    """
    Обёртка над add_operation: пишет доход.
    """
    add_operation(user_id, amount, category, date_str, "income")


def get_monthly_operations(user_id: int, op_type: str = None):
    """
    Возвращает операции пользователя за текущий месяц.
    op_type: 'expense' | 'income' | None (без фильтра).
    Возвращает кортежи (amount, category, date, type).
    """
    # Меняем формат на 'YYYY-MM', чтобы захватить весь текущий месяц
    current_month = datetime.now().strftime('%Y-%m')

    query = """
            SELECT amount, category, date, type
            FROM expenses
            WHERE user_id = ? AND date LIKE ? 
            """
    # Ищем все записи, дата которых начинается с текущего года и месяца (например, '2026-10%')
    params = [user_id, f"{current_month}%"]

    if op_type is not None:
        query += " AND type = ?"
        params.append(op_type)

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

def get_monthly_expenses(user_id: int):
    return get_monthly_operations(user_id, op_type='expense')

def get_monthly_incomes(user_id: int):
    return get_monthly_operations(user_id, op_type='income')