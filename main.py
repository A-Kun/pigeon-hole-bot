import logging
import os
import random
import re
import requests

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)


def get_pic_list(path):
    result = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png"):
                file_path = os.path.join(root, file)
                size = file_size(file_path)
                if "KB" in size and float(size.split()[0]) <= 756:
                    result.append(file_path)
    return result


def get_remote_image_url():
    content = requests.get('https://yande.re/post/popular_recent').content.decode('utf-8')
    all_pics = re.findall('id="p(\d+)"', content)
    pic = random.choice(all_pics)
    content = requests.get('https://yande.re/post/show/' + pic).content.decode('utf-8')
    image_url = re.findall('src="(https://files.yande.re/.+)"', content)[0]
    return image_url


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    bot.send_message(chat_id=update.message.chat_id, text='Hi!')


def help(bot, update):
    """Send a message when the command /help is issued."""
    bot.send_message(chat_id=update.message.chat_id, text='Help!')


def setu(bot, update):
    if (random.random() < 0.5):
        pic_list = get_pic_list("../pigeon-hole-bot-media")
        if len(pic_list) > 0:
            with open(random.choice(pic_list), "rb") as pic:
                bot.send_photo(chat_id=update.message.chat_id, photo=pic)
    else:
        image_url = get_remote_image_url()
        bot.send_photo(chat_id=update.message.chat_id, photo=image_url)


def error(bot, update):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    with open('.env') as env:
        updater = Updater(env.read().strip())

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("色图", setu))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
