from configparser import ConfigParser

config = ConfigParser()
config.read("conf.ini")

print(config['BOT']['TOKEN'])

