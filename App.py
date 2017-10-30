import os
import googlemaps
import DBqueries
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

gmaps = googlemaps.Client(key='AIzaSyDXNQpAsqsaii_Xxvu5tRf6dfHSasLl1WI')
conn = None


def start(bot, update):
    update.message.reply_text('Hi! This is Uneatable bot!')
    update.message.reply_text('Send /help for additional information!')
    user = DBqueries.select_user(update.message.from_user.id)
    if user is None:
        update.message.reply_text('Oh! You are a new user! Thank you for joining us!')
        update.message.reply_text('Please, send your location!')
        DBqueries.insert_user(update.message.from_user.id, None, None)
    else:
        update.message.reply_text('Send the name of the place or name of the dish!')


def update_location(bot, update):
    update.message.reply_text('We are going to reset your location!')
    DBqueries.update_user(update.message.from_user.id, None, None)
    update.message.reply_text('Please, send your new location!')


def help(bot, update):
    update.message.reply_text('Send /location to change your current location!')


def location(bot, update):
    user_location = update.message.location
    lat = user_location['latitude']
    long = user_location['longitude']
    DBqueries.update_user(update.message.from_user.id, lat, long)
    update.message.reply_text('Now you can send the name of the place or name of the dish!')


def places(bot, update):
    user_id = update.message.from_user.id
    types = ['food', 'bar', 'cafe']

    user = DBqueries.select_user(user_id)
    if user[1] is None or user[2] is None:
        update.message.reply_text('Please, send your location!')
        return
    else:
        lat = user[1]
        long = user[2]

    if len(update.message.text) == 1:
        emoji = DBqueries.select_emoji(update.message.text)
        if emoji is not None:
            update.message.text = emoji[0]
        else:
            update.message.reply_text('Wrong message! It is empty or you send wrong emoji! Try again!')
            return

    directions_result = gmaps.places_nearby(location=(lat, long), radius='5000', keyword=update.message.text,
                                            type=types)

    if len(directions_result['results']) == 0:
        update.message.reply_text('No restaurants were found! Try again!')
        return

    global List
    List = "List of restaurants:\n"
    for direct in directions_result['results']:
        List += "🍽 " + direct['name'] + " | " + direct['vicinity'] + "\n"
    update.message.reply_text(List)
    update.message.reply_text('Have a nice meal! 🍴')


def main():
    token = "467258132:AAHgTwdqU1LXxorqaluE0YqNAqzq2_p-WFo"
    port = int(os.environ.get('PORT', '5000'))
    updater = Updater(token)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("location", update_location))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.text, places))
    dp.add_handler(MessageHandler(Filters.location, location))
    updater.start_webhook(listen="0.0.0.0",
                          port=port,
                          url_path=token)

    updater.bot.set_webhook("https://uneatable.herokuapp.com/" + token)
    updater.idle()


if __name__ == '__main__':
    conn = DBqueries.connect_to_db()
    main()
