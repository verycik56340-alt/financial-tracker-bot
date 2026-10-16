from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Adding Income")],
        [KeyboardButton(text="Operation history"),
         KeyboardButton(text="Add expense")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Choose an option..."
)

#EXPENSE CATEGORIES
category_expense = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🍔 Groceries", callback_data="Food"),
            InlineKeyboardButton(text="☕ Cafe & Dining", callback_data="Cafe"),
        ],
        [
            InlineKeyboardButton(
                text="🚌 Transport", callback_data="Transport"
            ),
            InlineKeyboardButton(
                text="⛽ Car & Fuel", callback_data="Auto"
            ),
        ],
        [
            InlineKeyboardButton(text="🏠 Housing", callback_data="Housing"),
            InlineKeyboardButton(text="📱 Bills & Utilities", callback_data="Mobile"),
        ],
        [
            InlineKeyboardButton(
                text="💊 Health & Pharmacy", callback_data="Health"
            ),
            InlineKeyboardButton(
                text="🏋️ Sport & Fitness", callback_data="Sport"
            ),
        ],
        [
            InlineKeyboardButton(
                text="👕 Clothes & Shoes", callback_data="Clothes"
            ),
            InlineKeyboardButton(text="🛍️ Shopping", callback_data="Shopping"),
        ],
        [
            InlineKeyboardButton(
                text="🎬 Entertainment", callback_data="Entertainment"
            ),
            InlineKeyboardButton(
                text="🎮 Subscriptions", callback_data="Subscriptions"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🎓 Education & Books", callback_data="Education"
            ),
            InlineKeyboardButton(
                text="🎁 Gifts & Donations", callback_data="Gifts"
            ),
        ],
        [InlineKeyboardButton(text="📦 Other", callback_data="Other Expense")],
    ]
)

#INCOME CATEGORIES
category_income = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="💼 Salary", callback_data="Salary"),
            InlineKeyboardButton(text="💻 Freelance", callback_data="Freelance"),
        ],
        [
            InlineKeyboardButton(
                text="📈 Investments", callback_data="Invest"
            ),
            InlineKeyboardButton(
                text="🎁 Gift", callback_data="Gift Income"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔄 Cashback & Refunds", callback_data="Cashback"
            ),
            InlineKeyboardButton(text="📦 Other", callback_data="Other Income"),
        ],
    ]
)