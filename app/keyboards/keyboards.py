from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

main_kb = [
    [KeyboardButton(text="test"),
     KeyboardButton(text="TEST")]
]

main = ReplyKeyboardMarkup(keyboard=main_kb,
                           resize_keyboard=True,
                           input_field_placeholder="Выберите")

inline_kb_accept = [
    [InlineKeyboardButton(text="ПРИНЯТЬ", callback_data="accept_order"),
     InlineKeyboardButton(text="ОТМЕНИТЬ", url="https://ya.ru")]
]

inline_kb_send_to_delivery = [
    [InlineKeyboardButton(text="Отправить в доставку".upper(), callback_data="send_to_delivery")],
    [InlineKeyboardButton(text="Отменить".upper(), url="https://ya.ru")]
]

inline_kb_confirm_send_to_delivery = [
    [InlineKeyboardButton(text="Подвердить".upper(), callback_data="confirm_send_to_delivery"),
     InlineKeyboardButton(text="Отменить".upper(), url="https://ya.ru")]
]

inline_kb_cancel_delivery = [
    [InlineKeyboardButton(text="Отменить доставку".upper(), callback_data="cancel_delivery")]
]

inline_accept = InlineKeyboardMarkup(inline_keyboard=inline_kb_accept)
inline_send_to_delivery = InlineKeyboardMarkup(inline_keyboard=inline_kb_send_to_delivery)
inline_confirm_send_to_delivery = InlineKeyboardMarkup(inline_keyboard=inline_kb_confirm_send_to_delivery)
inline_cancel_delivery = InlineKeyboardMarkup(inline_keyboard=inline_kb_cancel_delivery)
