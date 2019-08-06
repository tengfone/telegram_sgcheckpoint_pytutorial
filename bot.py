import logging
import os
import requests
import sys

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# set path env TOKEN='XXX' and MODE = dev/prod

# logger
logger = logging.getLogger()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# global variable
mode = os.getenv("MODE")  # set in path env
TOKEN = os.getenv("TOKEN")  # set in path env
api_key = os.getenv("API_KEY")  # set in path env
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# options to run
if mode == "dev":
    def run(updater):
        updater.start_polling()
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
else:
    logger.error("MODE not specified")
    sys.exit(1)


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Click /camera or /rates")


def camera(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="/Woodlands or /Tuas ?")


def woodlands(update, context):
    response = requests.get('https://api.data.gov.sg/v1/transport/traffic-images').json()
    lta_raw_data = response['items'][0]
    lta_data = lta_raw_data['cameras']  # a list
    for each_dict in lta_data:
        if '2701' in each_dict.values():  # Woodlands Causeway (Towards Johor)
            woodlands_johor = each_dict
        if '2702' in each_dict.values():  # Woodlands Checkpoint (Towards BKE)
            woodlands_bke = each_dict

    woodlands_johor_image = woodlands_johor['image']
    woodlands_johor_timestamp = woodlands_johor['timestamp'].replace('T', ' ')[:-6]
    context.bot.send_message(chat_id=update.message.chat_id, text='Woodlands Causeway (Towards Johor)')
    context.bot.send_photo(chat_id=update.message.chat_id, photo=woodlands_johor_image)
    context.bot.send_message(chat_id=update.message.chat_id, text='Last Updated at ' + woodlands_johor_timestamp)

    woodlands_bke_image = woodlands_bke['image']
    woodlands_bke_timestamp = woodlands_bke['timestamp'].replace('T', ' ')[:-6]
    context.bot.send_message(chat_id=update.message.chat_id, text='Woodlands Checkpoint (Towards BKE)')
    context.bot.send_photo(chat_id=update.message.chat_id, photo=woodlands_bke_image)
    context.bot.send_message(chat_id=update.message.chat_id, text=('Last Updated at ' + woodlands_bke_timestamp))


def tuas(update, context):
    response = requests.get('https://api.data.gov.sg/v1/transport/traffic-images').json()
    lta_raw_data = response['items'][0]
    lta_data = lta_raw_data['cameras']  # a list
    for each_dict in lta_data:
        if '4703' in each_dict.values():  # Second Link at Tuas
            tuas_link = each_dict
        if '4713' in each_dict.values():  # Tuas Checkpoint
            tuas_checkpoint = each_dict

    tuas_link_image = tuas_link['image']
    tuas_link_timestamp = tuas_link['timestamp'].replace('T', ' ')[:-6]
    context.bot.send_message(chat_id=update.message.chat_id, text='Second Link at Tuas')
    context.bot.send_photo(chat_id=update.message.chat_id, photo=tuas_link_image)
    context.bot.send_message(chat_id=update.message.chat_id, text=('Last Updated at ' + tuas_link_timestamp))

    tuas_checkpoint_image = tuas_checkpoint['image']
    tuas_checkpoint_timestamp = tuas_checkpoint['timestamp'].replace('T', ' ')[:-6]
    context.bot.send_message(chat_id=update.message.chat_id, text='Tuas Checkpoint')
    context.bot.send_photo(chat_id=update.message.chat_id, photo=tuas_checkpoint_image)
    context.bot.send_message(chat_id=update.message.chat_id, text=('Last Updated at ' + tuas_checkpoint_timestamp))


def rates(update, context):
    website = 'https://free.currconv.com/api/v7/convert?q=SGD_MYR,MYR_SGD&compact=ultra&apiKey={}'
    currency = requests.get(website.format(api_key)).json()
    sgd_to_myr = currency.get('SGD_MYR')
    context.bot.send_message(chat_id=update.message.chat_id,
                             text='The current exchange rate from SGD to MYR is ' + str(sgd_to_myr))


def unknownCommand(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Sorry I stupid. I don't understand the command.")


def unknownText(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Sorry I stupid. I don't understand that text.")


if __name__ == '__main__':
    logger.info("Starting bot")

    # to start the bot
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    # camera function
    start_handler = CommandHandler('camera', camera)
    dispatcher.add_handler(start_handler)

    # woodlands side
    start_handler = CommandHandler('Woodlands', woodlands)
    dispatcher.add_handler(start_handler)

    # tuas side
    start_handler = CommandHandler('Tuas', tuas)
    dispatcher.add_handler(start_handler)

    # rates
    start_handler = CommandHandler('rates', rates)
    dispatcher.add_handler(start_handler)

    # unknown commands
    unknown_handler = MessageHandler(Filters.command, unknownCommand)
    dispatcher.add_handler(unknown_handler)

    # unknown commands
    unknown_handler = MessageHandler(Filters.text, unknownText)
    dispatcher.add_handler(unknown_handler)

    run(updater)
