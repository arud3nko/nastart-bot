from app.bot.bot import bot
from app.keyboards.keyboards import inline_accept

from aiogram.enums import ParseMode


async def format_order_message(data):
    shop = data["shop"]
    customer = data["customer"]
    order = data["order"]
    delivery = data["delivery"]

    order_items = "\n".join(
        [f"{item['quantity']} x {item['title']} = {item['price']} руб." for item in order["products"]])
    total_order_price = f"{order['price']} руб."
    user_payment = f"{order['payment_type']}"

    message = f"*Новый заказ* [№{order['wc_id']}]\n\n"
    message += f"*Клиент*: {customer['name']}\n"
    message += f"*Адрес*: {delivery['address']} \n*Телефон*: {customer['contact_phone']}\n"
    message += f"*Примечание клиента*: {order['customer_note']}\n\n"
    message += f"{order_items}\n\n"
    message += f"*Стоимость заказа:* {total_order_price}\n"
    message += f"Стоимость доставки, оплаченная пользователем: {delivery['price']} руб.\n\n"
    message += f"*Итог*: {int(float(order['price']) + float(delivery['price']))} руб.\n\n"
    message += f"*Доставка:* {delivery['type']} ({shop['address']})\n"
    message += f"*Оплата:* {user_payment}"

    return message


async def new_order_handler(request) -> None:
    data = await request.json()
    message_text = await format_order_message(data)

    await bot.send_message(-4007410160, message_text, reply_markup=inline_accept, parse_mode=ParseMode.MARKDOWN)

