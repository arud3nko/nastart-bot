import logging
import sys

from aiohttp import web

from aiogram import Dispatcher, Router, Bot
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.enums.update_type import UpdateType

from app.bot.bot import bot
from app.handlers.new_order import new_order_handler
from app.handlers import order_actions
# from app.config.config import BASE_WEBHOOK_URL


WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 8080

WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = "my-secret"
BASE_WEBHOOK_URL = "https://cf0e-37-147-31-102.ngrok-free.app"

router = Router()


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET,
                          allowed_updates=[UpdateType.MESSAGE,
                                           UpdateType.CALLBACK_QUERY])


def main() -> None:
    # Dispatcher is a root router
    dp = Dispatcher()
    dp.include_routers(router,
                       order_actions.router)

    dp.startup.register(on_startup)

    app = web.Application()
    app.add_routes([web.post('/new_order', new_order_handler)])

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
