from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

main_kb = [
    [KeyboardButton(text="test"),
     KeyboardButton(text="TEST")]
]

main = ReplyKeyboardMarkup(keyboard=main_kb,
                           resize_keyboard=True,
                           input_field_placeholder="Выберите")


def build_kb_accept(ID: int) -> InlineKeyboardMarkup:
    inline_kb_accept = [
        [InlineKeyboardButton(text="Принять".upper(), callback_data=f"accept_order::{ID}")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_kb_accept)


def build_kb_send_to_delivery(ID: int) -> InlineKeyboardMarkup:
    inline_kb_send_to_delivery = [
        [InlineKeyboardButton(text="Отправить в доставку".upper(), callback_data=f"send_to_delivery::{ID}")],
        [InlineKeyboardButton(text="Отменить".upper(), callback_data=f"cancel_delivery::{ID}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_send_to_delivery)


def build_kb_confirm_delivery(ID: int) -> InlineKeyboardMarkup:
    inline_kb_confirm_send_to_delivery = [
        [InlineKeyboardButton(text="Подтвердить".upper(), callback_data=f"confirm_delivery::{ID}"),
         InlineKeyboardButton(text="Отменить".upper(), callback_data=f"cancel_delivery::{ID}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_confirm_send_to_delivery)


def build_kb_cancel_delivery(ID: int) -> InlineKeyboardMarkup:
    inline_kb_cancel_delivery = [
        [InlineKeyboardButton(text="Отменить доставку".upper(), callback_data=f"cancel_delivery::{ID}")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_kb_cancel_delivery)

def build_kb_sure_cancel_delivery(ID: int) -> InlineKeyboardMarkup:
    inline_kb_sure_cancel_delivery = [
        [InlineKeyboardButton(text="Подтвердить".upper(), callback_data=f"cancel_delivery_sure::{ID}")],
        [InlineKeyboardButton(text="Не отменять".upper(), callback_data=f"cancel_delivery_deny::{ID}")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_kb_sure_cancel_delivery)
