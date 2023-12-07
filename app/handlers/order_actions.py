from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from datetime import datetime, timezone

from contextlib import suppress

from app.keyboards.keyboards import (build_kb_send_to_delivery,
                                     build_kb_confirm_delivery,
                                     build_kb_cancel_delivery,
                                     build_kb_sure_cancel_delivery)

from app.yandexDelivery.order import Order

import pytz
import logging

router = Router()

logging.basicConfig(filename='orders.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


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
    with suppress(TelegramBadRequest):
        await callback.message.delete()

    order_id = int(callback.data.split("::")[1])
    order = Order(orders_table_name='orders')
    await order.from_db(ID=order_id)
    await order.update_status("send_to_delivery")
    await order.create_claim()
    await order.update_status("claim_created")

    logging.info(f"Successfully created claim {order.id} x {order.delivery_id}")

    delivery_price = await order.get_new_order_price()

    logging.info(f"Received price for {order.id} x {order.delivery_id}: {delivery_price}")

    message = await callback.message.answer(
        f"*Доставка заказа* [№{order.order_wc_id}] от {order.order_created_time}\n\n"
        f"*Стоимость доставки:* {int(float(delivery_price))} руб.\n\n"
        "*Подтвердить отправку в доставку?*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=build_kb_confirm_delivery(order_id)
    )

    await callback.answer()

    if await order.check_order_confirmed() == 'validate_time_out':
        await order.cancel()
        await order.update_status("accepted")

        await order.db.delete('delivery', 'order_id', order_id)

        await message.edit_text(
            f"*Доставка заказа* [№{order.order_wc_id}] от {order.order_created_time}\n\n"
            f"*Стоимость доставки* больше не актуальна.\n\n"
            "Для перерасчета стоимости нажмите \n*Отправить в доставку*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_kb_send_to_delivery(order_id)
        )


@router.callback_query(F.data.startswith("confirm_delivery::"))
async def confirm_delivery_handler(callback: types.CallbackQuery):
    order_id = int(callback.data.split("::")[1])
    order = Order(orders_table_name='orders')
    await order.from_db(ID=order_id)

    if await order.confirm_delivery():
        await order.update_status("delivery_confirmed")

        logging.info(f"[DELIVERY] Confirmed {order.id} x {order.delivery_id}")

        message = await callback.message.answer(
            f"*Доставка заказа* [№{order.order_wc_id}] от {order.order_created_time}\n\n"
            "*Заказ отправлен в доставку*, Вам поступит уведомление, когда будет найден курьер.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_kb_cancel_delivery(order_id))

        with suppress(TelegramBadRequest):
            await callback.message.delete()

        await callback.answer()

        courier_info, route_points = await order.get_courier_info()

        logging.info(f"[DELIVERY] Courier found {order.id} x {order.delivery_id}")

        courier_car_number = courier_info['car_number'] if len(courier_info['car_number']) <= 9 else "Без номера"

        shop_tz = pytz.timezone(order.order_created_timezone)
        pickup_to = str(route_points[0]['expected_visit_interval']['to'])
        deliver_to = str(route_points[1]['expected_visit_interval']['to'])

        pickup_to_form = pickup_to.split('T')[0] + 'T' + pickup_to.split('T')[1]
        deliver_to_form = deliver_to.split('T')[0] + 'T' + deliver_to.split('T')[1]

        pickup_to_form = datetime.fromisoformat(pickup_to_form)
        pickup_to = pickup_to_form.astimezone(shop_tz)
        pickup_to = pickup_to.strftime("%H:%M")

        deliver_to_form = datetime.fromisoformat(deliver_to_form)
        deliver_to = deliver_to_form.astimezone(shop_tz)
        deliver_to = deliver_to.strftime("%H:%M")

        courier_phone_number, courier_extended_number = await order.get_courier_phone_number()

        await message.answer(
            f"*Доставка заказа* [№{order.order_wc_id}] от {order.order_created_time}\n\n"
            f"*Найден курьер!*\n\n"
            f"*Имя:* {courier_info['courier_name']}\n"
            f"*Телефон:* {courier_phone_number} доб. {courier_extended_number}\n"
            f"*Приедет на* {courier_info['car_color']} {courier_info['car_model']}\n"
            f"*Номер авто:* {courier_car_number}\n"
            f"*Прибудет в ресторан до* {pickup_to}\n"
            f"*Прибудет к гостю до* {deliver_to}\n\n"
            f"ID заказа: {order.id} x {order.delivery_id}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=None
        )

        await order.update_status('delivering')

        with suppress(TelegramBadRequest):
            await message.delete()


@router.callback_query(F.data.startswith("cancel_delivery::"))
async def cancel_delivery_handler(callback: types.CallbackQuery):
    """

    > 8.12.2023
        Дополнительное подтверждение отмены доставки, добавлено так как нередко администраторы случайно нажимают
        кнопку отмены

    :param callback:
    :return:
    """
    order_id = int(callback.data.split("::")[1])
    order = Order(orders_table_name='orders')
    await order.from_db(ID=order_id)

    await callback.message.answer(f"*Доставка заказа* [№{order.order_wc_id}] от {order.order_created_time}\n\n"
                                  "*Вы уверены, что хотите ОТМЕНИТЬ доставку?* ",
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=build_kb_sure_cancel_delivery(order_id))

    with suppress(TelegramBadRequest):
        await callback.message.delete()

    await callback.answer()


@router.callback_query(F.data.startswith("cancel_delivery_sure::"))
async def sure_cancel_delivery_handler(callback: types.CallbackQuery):
    """

    > 8.12.2023
        Отмена доставки после подтверждения

    :param callback:
    :return:
    """
    order_id = int(callback.data.split("::")[1])
    order = Order(orders_table_name='orders')
    await order.from_db(ID=order_id)
    await order.cancel()
    await order.update_status('delivery_cancelled')

    await callback.message.answer(f"*Доставка заказа* [№{order.order_wc_id}] от {order.order_created_time}\n\n"
                                  "*Доставка отменена* ",
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=None)

    with suppress(TelegramBadRequest):
        await callback.message.delete()

    await callback.answer()


@router.callback_query(F.data.startswith("cancel_delivery_deny::"))
async def sure_cancel_delivery_handler(callback: types.CallbackQuery):
    """

    > 8.12.2023
        Отмена отмены доставки (если не подтвердили доставку)

    :param callback:
    :return:
    """
    order_id = int(callback.data.split("::")[1])
    order = Order(orders_table_name='orders')
    await order.from_db(ID=order_id)

    with suppress(TelegramBadRequest):
        await callback.message.delete()

    await callback.answer()
