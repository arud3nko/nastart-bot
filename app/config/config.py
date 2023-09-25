from configparser import ConfigParser
import os

config = ConfigParser()
config.read("./conf.ini")

TOKEN = config["BOT"]["TOKEN"]
BASE_WEBHOOK_URL = config["SERVER"]["BASE_WEBHOOK_URL"]
