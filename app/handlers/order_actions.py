from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest

from contextlib import suppress

from app.keyboards.keyboards import (build_kb_send_to_delivery,
                                     build_kb_confirm_delivery,
                                     inline_cancel_delivery)

from app.yandexDelivery.order import Order

router = Router()


@router.callback_query(F.data.startswith("accept_order::"))
async def accept_order_handler(callback: types.CallbackQuery):
    order_id = int(callback.data.split("::")[1])
    order = Order(orders_table_name='orders')
    await order.from_db(ID=order_id)
    await order.update_status("accepted")

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer(f"*Новый заказ* [№{order.order_wc_id}] от {order.order_created_time}\n\n"
                                  "*Заказ принят.* По готовности нажмите кнопку «Отправить в доставку»",
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=build_kb_send_to_delivery(order_id))
    await callback.answer(text="По готовности нажмите\nОтправить в доставку", show_alert=True)


@router.callback_query(F.data.startswith("send_to_delivery::"))
async def send_to_delivery_handler(callback: types.CallbackQuery):
    order_id = int(callback.data.split("::")[1])
    order = Order(orders_table_name='orders')
    await order.from_db(ID=order_id)
    await order.update_status("send_to_delivery")

    await callback.message.answer(f"*Доставка заказа* [№{order.order_wc_id}] от {order.order_created_time}\n\n"
                                  "*Стоимость доставки:* 334,56 руб.\n\n"
                                  "*Подтвердить отправку в доставку?*",
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=build_kb_confirm_delivery(order_id))

    with suppress(TelegramBadRequest):
        await callback.message.delete()

    await callback.answer()


@router.callback_query(F.data == "confirm_delivery")
async def send_to_delivery_handler(callback: types.CallbackQuery):
    await callback.message.answer("*Доставка заказа [No1234]* от 14.09.2023 18:31\n\n "
                                  "*Заказ отправлен в доставку*, Вам поступит уведомление, когда будет найден курьер.",
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=inline_cancel_delivery)

    with suppress(TelegramBadRequest):
        await callback.message.delete()

    await callback.answer()
