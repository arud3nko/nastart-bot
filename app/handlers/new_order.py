import json

from app.bot.bot import bot
from app.keyboards.keyboards import build_kb_accept
from app.yandexDelivery.order import Order

from typing import Any

from aiogram.enums import ParseMode


def format_message(newOrder: Order) -> str:
    order_items = "\n".join(
        [f"*{item['quantity']} x {item['title']} = {item['price']} руб.*" for item in
         json.loads(newOrder.order_products)])

    new_order_message = \
        f"""
*Новый заказ* [№{newOrder.order_wc_id}] от {newOrder.order_created_time}

*Клиент:* {newOrder.customer_name}
*Телефон:* {newOrder.customer_contact_phone}
Примечание клиента: {newOrder.order_customer_note}

{order_items}

*Стоимость заказа:* {newOrder.order_price} руб.
Стоимость доставки, оплаченная пользователем: {newOrder.delivery_price} руб.

*Итог*: {int(float(newOrder.order_price) + float(newOrder.delivery_price))} руб.
{newOrder.order_payment_method_title}

Доставка: {newOrder.delivery_type} ({newOrder.delivery_address})
            """

    return new_order_message


async def format_dict(json_request: Any) -> dict:
    data = {
        'shop_id': json_request['shop']['id'],
        'shop_secret_key': json_request['shop']['secret'],
        'shop_tg_group_id': json_request['shop']['tg_group_id'],
        'shop_title': json_request['shop']['title'],
        'shop_latitude': json_request['shop']['coords'][0],
        'shop_longitude': json_request['shop']['coords'][1],
        'shop_contact_phone': json_request['shop']['contact_phone'],
        'shop_address': json_request['shop']['address'],
        'customer_name': json_request['customer']['name'],
        'customer_contact_phone': json_request['customer']['contact_phone'],
        'order_wc_id': json_request['order']['wc_id'],
        'order_products': json.dumps(json_request['order']['products'], ensure_ascii=False),
        'order_customer_note': json_request['order']['customer_note'],
        'order_price': json_request['order']['price'],
        'order_payment_method_title': json_request['order']['payment_type'],
        'order_created_time': json_request['order']['created_time'],
        'delivery_type': json_request['delivery']['type'],
        'delivery_price': json_request['delivery']['price'],
        'delivery_address': json_request['delivery']['address'],
        'delivery_latitude': json_request['delivery']['coords'][0],
        'delivery_longitude': json_request['delivery']['coords'][1],
        'delivery_api_key': json_request['delivery']['api_key'],
        'delivery_geo_key': json_request['delivery']['geo_key']
    }

    return data


async def new_order_handler(request) -> None:
    data = await format_dict(await request.json())

    newOrder = Order(orders_table_name='orders')
    new_order_id = await newOrder.new_order(data)

    new_order_message = format_message(newOrder)

    await newOrder.from_db(new_order_id)

    await bot.send_message(newOrder.shop_tg_group_id,
                           new_order_message,
                           reply_markup=build_kb_accept(new_order_id),
                           parse_mode=ParseMode.MARKDOWN)
