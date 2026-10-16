import math

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.filters.command import Command, CommandStart
from datetime import datetime
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
import keyboards as kb
from database import add_expense, get_monthly_expenses, add_income, get_monthly_incomes
from collections import defaultdict

user = Router()

class Form(StatesGroup):
    waiting_for_amount_expense = State()
    waiting_for_amount_income = State()
    waiting_for_category_expense  = State()
    waiting_for_category_income = State()

MAX_AMOUNT = 1_000_000_000
AMOUNT_PROMPT = (
    "Please enter a positive amount as a number up to 1 000 000 000, "
    "for example 12.50 or 12,50."
)


def parse_amount(text) -> float | None:
    """
    Validates user input as a positive monetary amount.
    Accepts a dot or a comma as the decimal separator, rounds to 2 decimals.
    Returns None for anything that is not a valid amount.
    """
    if not text:
        return None
    try:
        value = float(text.strip().replace(",", "."))
    except ValueError:
        return None
    if not math.isfinite(value) or value <= 0 or value > MAX_AMOUNT:
        return None
    return round(value, 2)


EXPENSE_CATEGORIES = frozenset(
    button.callback_data
    for row in kb.category_expense.inline_keyboard
    for button in row
)
INCOME_CATEGORIES = frozenset(
    button.callback_data
    for row in kb.category_income.inline_keyboard
    for button in row
)

# Greeting
@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_name = message.from_user.first_name if message.from_user else None
    await message.answer(f"Hello {user_name or 'there'}! I help you track income and expenses!",
                         reply_markup=kb.menu)


# Cancel the current scenario (works in any state)
@user.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Cancelled", reply_markup=kb.menu)



# Ask for the expense amount
@user.message(F.text == "Add expense")
async def cmd_add_expense(message: Message, state: FSMContext):
    await message.answer("Enter the amount: ")
    await state.set_state(Form.waiting_for_amount_expense)

# Save the amount and ask for the category
@user.message(Form.waiting_for_amount_expense)
async def process_amount_expense(message: Message, state: FSMContext):
    amount = parse_amount(message.text)
    if amount is None:
        await message.answer(AMOUNT_PROMPT)
        return

    await state.update_data(amount_expense=amount)

    await message.answer(
        "Great! Now select a category:",
        reply_markup=kb.category_expense
    )
    await state.set_state(Form.waiting_for_category_expense)

# Handle an inline button press while waiting for the category
@user.callback_query(Form.waiting_for_category_expense, F.data.in_(EXPENSE_CATEGORIES))
async def process_category_expense(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    await state.update_data(category=callback.data)

    data = await state.get_data()
    amount_expense = data.get("amount_expense")
    if amount_expense is None:
        await callback.answer("Outdated button", show_alert=False)
        await state.clear()
        return
    category_expense = data.get("category")

    add_expense(
        user_id=callback.from_user.id,
        amount=amount_expense,
        category=category_expense,
        date_str=current_time,
    )

    await callback.message.answer("✅ The expense has been successfully saved to the database!")
    await state.clear()

# Show the operation history
@user.message(F.text == "History")
async def show_monthly_report(message: Message):
    user_id = message.from_user.id
    expenses = get_monthly_expenses(user_id)
    incomes = get_monthly_incomes(user_id)

    if not expenses and not incomes:
        await message.answer(
            "❌ You haven't recorded any transactions yet this month."
        )
        return

    report = "📅 Your transactions for this month:\n\n"

    total_expenses_ops = len(expenses)
    total_incomes_ops = len(incomes)

    total_sum_expense = 0
    total_sum_income = 0

    aggregation_expense = defaultdict(lambda: {"sum": 0, "count": 0})
    aggregation_income = defaultdict(lambda: {"sum": 0, "count": 0})

    for amount, category, *_ in expenses:
        aggregation_expense[category]["sum"] += amount
        aggregation_expense[category]["count"] += 1
        total_sum_expense += amount

    for amount, category, *_ in incomes:
        aggregation_income[category]["sum"] += amount
        aggregation_income[category]["count"] += 1
        total_sum_income += amount

    sorted_aggregation_expense = sorted(
        aggregation_expense.items(),
        key=lambda item: item[1]["sum"],
        reverse=True,
    )
    sorted_aggregation_income = sorted(
        aggregation_income.items(),
        key=lambda item: item[1]["sum"],
        reverse=True,
    )

    if sorted_aggregation_expense:
        report += "📊 Expenses by category:\n"
        for category, stats in sorted_aggregation_expense:
            report += f"📁 {category}: -{stats['sum']:.2f} | ({stats['count']} ops)\n"
        report += "\n"

    if sorted_aggregation_income:
        report += "📊 Incomes by category:\n"
        for category, stats in sorted_aggregation_income:
            report += f"📁 {category}: +{stats['sum']:.2f} | ({stats['count']} ops)\n"
        report += "\n"

    report += f"📊 Total expenses ops: {total_expenses_ops}\n"
    report += f"📊 Total incomes ops: {total_incomes_ops}\n"
    report += f"💵 Total amount expense: -{total_sum_expense:.2f}\n"
    report += f"💵 Total amount incomes: +{total_sum_income:.2f}\n"
    report += f"🏦 Balance: {total_sum_income - total_sum_expense:+.2f}"

    await message.answer(report)

# Ask for the income amount
@user.message(F.text == "Add income")
async def cmd_add_income(message: Message, state: FSMContext):
    await message.answer("Enter the amount: ")
    await state.set_state(Form.waiting_for_amount_income)

# Save the income amount and ask for the category
@user.message(Form.waiting_for_amount_income)
async def process_amount_income(message: Message, state: FSMContext):
    amount = parse_amount(message.text)
    if amount is None:
        await message.answer(AMOUNT_PROMPT)
        return

    await state.update_data(amount_income=amount)

    await message.answer(
        "Great! Now select a category:",
        reply_markup=kb.category_income
    )
    await state.set_state(Form.waiting_for_category_income)

# Handle an inline button press while waiting for the income category
@user.callback_query(Form.waiting_for_category_income, F.data.in_(INCOME_CATEGORIES))
async def process_category_income(callback: CallbackQuery, state: FSMContext):

    await callback.answer()

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    await state.update_data(category=callback.data)

    data = await state.get_data()
    amount_income = data.get("amount_income")
    if amount_income is None:
        await callback.answer("Outdated button", show_alert=False)
        await state.clear()
        return
    category_income = data.get("category")

    add_income(
        user_id=callback.from_user.id,
        amount=amount_income,
        category=category_income,
        date_str=current_time
    )

    await callback.message.answer("✅ The income has been successfully saved to the database!")
    await state.clear()


@user.message()
async def echo(message: Message):
    await message.send_copy(chat_id=message.from_user.id)

# Stale/foreign callback buttons: dismiss the "spinner" with a clear answer
@user.callback_query()
async def process_outdated_callback(callback: CallbackQuery):
    await callback.answer("Outdated button", show_alert=False)