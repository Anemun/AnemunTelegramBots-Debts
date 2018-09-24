import telebot
import databaseProvider
import argparse, sys
from sys import argv
from telebot import types
from datetime import datetime

parser=argparse.ArgumentParser()
parser.add_argument('--botToken', help='telegram bot token')
parser.add_argument('--databasePath', help='pathtoDatabase')
args=parser.parse_args()

TELEGRAM_BOT_TOKEN = args.botToken
DATABASE_FILE = args.databasePath

version = "1.2.0-20180924"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

databaseProvider.Init(DATABASE_FILE)
hideMarkup = types.ReplyKeyboardRemove()


@bot.message_handler(commands=["ver"])
def showVersion(message):
    reply = "текущая версия: {0}".format(version)
    bot.send_message(chat_id=message.chat.id, text=reply)


@bot.message_handler(commands=["history"])
def showHistory(message):
    databaseResult = databaseProvider.getHistory()
    text = ""
    for i in range(len(databaseResult)):
        text += str(databaseResult[i])
        text += "\n"
    bot.send_message(chat_id=message.chat.id,
                     text=text)


@bot.message_handler(commands=["help"])
def showHelp(message):
    bot.send_message(chat_id=message.chat.id,
                     text="Используйте фразу 'долг Кто Кому Сумма'\nНапример: 'долг Роман Пётр 500' - значит, Роман должен Петру 500р")


@bot.message_handler(commands=["debts"])
def showDebts(message):
    databaseResult = databaseProvider.getDebts()
    text = ""
    for i in range(len(databaseResult)):
        text += str(databaseResult[i])
        text += "\n"
    bot.send_message(chat_id=message.chat.id,
                     text=text)


@bot.message_handler(regexp='долг')
def confirmDebt(message):
    text = str.split(message.text, ' ')
    if len(text) == 4:
        keyboard = types.InlineKeyboardMarkup()
        button_yes = types.InlineKeyboardButton(text="Да", callback_data="writeDebtYes")
        button_no = types.InlineKeyboardButton(text="Нет", callback_data="writeDebtNo")
        keyboard.add(button_yes, button_no)
        text = str.format("Кто: {0}\n"
                          "Кому: {1}\n"
                          "Сколько: {2}\n"
                          "Записать данный долг?", text[1], text[2], text[3])
        bot.send_message(chat_id=message.chat.id,
                         text=text, reply_markup=keyboard)
    else:
        pass


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        raw = str.split(call.message.text, '\n')
        who = str.split(raw[0], ' ')[1]
        toWhom = str.split(raw[1], ' ')[1]
        debt = str.split(raw[2], ' ')[1]
        if call.data == "writeDebtYes":
            databaseProvider.writeToDatabase(who, toWhom, debt)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="Записано в базу!")
        if call.data == "writeDebtNo":
            bot.delete_message(chat_id=call.message.chat.id,
                               message_id=call.message.message_id)
        name = call.message.chat.id
        date = str(datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
        text = "{0} {1} {2}".format(who, toWhom, debt)
        databaseProvider.writeHistory(name, date, text)


if __name__ == '__main__':
    bot.polling(none_stop=True)
