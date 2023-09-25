from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest

from contextlib import suppress

from app.keyboards.keyboards import (inline_send_to_delivery,
                                     inline_confirm_send_to_delivery,
                                     inline_cancel_delivery)

router = Router()


@router.callback_query(F.data == "accept_order")
async def accept_order_handler(callback: types.CallbackQuery):
    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer("*Новый заказ* \n\n"
                                  "*Заказ принят.* По готовности нажмите кнопку «Отправить в доставку»",
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=inline_send_to_delivery)
    await callback.answer(text="По готовности нажмите\nОтправить в доставку", show_alert=True)


@router.callback_query(F.data == "send_to_delivery")
async def send_to_delivery_handler(callback: types.CallbackQuery):
    await callback.message.answer("*Доставка заказа [No1234]* от 14.09.2023 18:31\n\n "
                                  "*Стоимость доставки:* 334,56 руб.\n\n"
                                  "*Подтвердить отправку в доставку?*",
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=inline_confirm_send_to_delivery)

    with suppress(TelegramBadRequest):
        await callback.message.delete()

    await callback.answer()


@router.callback_query(F.data == "confirm_send_to_delivery")
async def send_to_delivery_handler(callback: types.CallbackQuery):
    await callback.message.answer("*Доставка заказа [No1234]* от 14.09.2023 18:31\n\n "
                                  "*Заказ отправлен в доставку*, Вам поступит уведомление, когда будет найден курьер.",
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=inline_cancel_delivery)

    with suppress(TelegramBadRequest):
        await callback.message.delete()

    await callback.answer()
