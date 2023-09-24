from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram import Router

main_kb = [
    [KeyboardButton(text="test"),
     KeyboardButton(text="TEST")]
]

main = ReplyKeyboardMarkup(keyboard=main_kb,
                           resize_keyboard=True,
                           input_field_placeholder="Выберите")

inline_kb = [
    [InlineKeyboardButton(text="ПРИНЯТЬ", url="https://ya.ru"),
     InlineKeyboardButton(text="ОТМЕНИТЬ", url="https://ya.ru")]
]

inline = InlineKeyboardMarkup(inline_keyboard=inline_kb)