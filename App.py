import googlemaps
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

import DBqueries


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


def favorite(bot, update):
    update.message.reply_text('Here are your favorite places!')
    favs = DBqueries.select_fav(update.message.from_user.id)
    result = "List of favorites:\n\n"
    for each in favs:
        result += "⭐️ " + each[0] + "\n\n"
    update.message.reply_text(result)

    

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

    cuisine = DBqueries.find_cuisine_by_dish(update.message.text)
    if cuisine is None:
        directions_result = gmaps.places_nearby(location=(lat, long), radius='3000', keyword=update.message.text,
                                                type=types)
    else:
        directions_result = gmaps.places_nearby(location=(lat, long), radius='3000', keyword=cuisine,
                                                type=types)

    if len(directions_result['results']) == 0:
        update.message.reply_text('No restaurants were found! Try again!')
        return

    list_of_places = []
    for direct in directions_result['results']:
        place_coordinates = direct['geometry']['location']
        dist = gmaps.distance_matrix([place_coordinates],
                                     [{"lat": lat, "lng": long}])
        res = [direct['name'], direct['vicinity'], dist['rows'][0]['elements'][0]['distance']['text'],
               dist['rows'][0]['elements'][0]['distance']['value']]
        list_of_places.append(res)
    list_of_places.sort(key=lambda x: x[2])
    list_of_places = list_of_places[:5]
    result = "List of restaurants:\n\n"
    for each in list_of_places:
        result += "🍴 " + each[0] + " | " + each[1] + " | " + each[2] + "\n\n"

    update.message.reply_text(result)
    update.message.reply_text('Have a nice meal! 🍴')

    list_of_buttons = []
    for i in range(0,len(list_of_places)):
        list_of_buttons.append([InlineKeyboardButton(list_of_places[i][0], callback_data=list_of_places[i][0])])

    reply_markup = InlineKeyboardMarkup(list_of_buttons)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query
    DBqueries.add_fav(query['message']['chat']['id'],query['data'])


def main():
    token = "467258132:AAHgTwdqU1LXxorqaluE0YqNAqzq2_p-WFo"
    # port = int(os.environ.get('PORT', '5000'))
    updater = Updater(token)

    dp = updater.dispatcher
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("favorite", favorite))
    dp.add_handler(CommandHandler("location", update_location))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.text, places))
    dp.add_handler(MessageHandler(Filters.location, location))
    # updater.start_webhook(listen="0.0.0.0",
    #                       port=port,
    #                       url_path=token)

    # updater.bot.set_webhook("https://uneatable.herokuapp.com/" + token)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    conn = DBqueries.connect_to_db()
    main()