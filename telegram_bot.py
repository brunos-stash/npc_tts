from os import isatty
from pathlib import Path
from telegram import Update, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultAudio, ChosenInlineResult, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, InlineQueryHandler, CallbackQueryHandler, commandhandler
import tts
from utils import is_admin
import logging
from uuid import uuid4
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def synthesize(update: Update, context: CallbackContext) -> None:
    text = update.message.text.split('/tts ')[1]
    file_path = tts.synthesize(text)
    file_path = tts.add_padding(file_path, Path('data/background/npc.mp3'))
    with open(file_path, 'rb') as f:
        _audio = f.read()
        # update.message.reply_audio(audio=_audio, title=text, caption=update.message.from_user.first_name, filename=text+".mp3")
        # update.message.chat_id
        context.bot.send_audio(audio=_audio, chat_id=update.message.chat_id, title=text, caption=update.message.from_user.first_name, filename=text+".mp3")
    update.message.delete()
    
def inline_caps(update: Update, context: CallbackContext):
    query = update.inline_query.query
    if not query:
        return
    if not is_admin(update.inline_query.from_user.id):
        return
    groups = context.bot_data["groups"]
    results = list()
    for k,v in groups.items():
        results.append(
            InlineQueryResultArticle(
                id=v["title"], 
                title=v["title"], 
                input_message_content=InputTextMessageContent(v["title"])
            )
        )
    # results.append(
    #     InlineQueryResultArticle(
    #         id=query.upper(),
    #         title='kk',
    #         input_message_content=InputTextMessageContent(query.upper())
    #     )
    # )
    # update.inline_query.from_user.send_message("fff")
    context.bot.answer_inline_query(update.inline_query.id, results)

def test(update: Update, context: CallbackContext):
    if not is_admin(update.message.from_user.id):
        return
    if update.message.chat.type == 'private':
        update.message.reply_text(str(context.bot_data["groups"]))
        context.bot.send_message(-1001701137469, "teeeest")

    # if update.message.chat.id == -1001701137469:
    if not context.bot_data.get("groups", None):
        chat_id = str(update.message.chat.id)
        chat = update.message.chat.to_dict()
        context.bot_data["groups"] = {chat_id: chat}
    else:
        chat_id = str(update.message.chat.id)
        chat = update.message.chat.to_dict()
        context.bot_data["groups"][chat_id] = chat
        # update.message.reply_text('works here')    

def start(update: Update, context: CallbackContext) -> None:
    """Sends a message with three inline buttons attached."""
    if not is_admin(update.message.from_user.id):
        return
    keyboard = [
        [
            InlineKeyboardButton("Option 1", callback_data='1'),
            InlineKeyboardButton("Option 2", callback_data='2'),
        ],
        [InlineKeyboardButton("Option 3", callback_data='3')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(text=f"Selected option: {query.data}")

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    with open('api.token', 'r') as f:
        token = f.readlines()
    updater = Updater(token[0].strip(), use_context=True)
    updater.dispatcher.add_handler(CommandHandler('tts', synthesize))
    updater.dispatcher.add_handler(CommandHandler('test', test))
    updater.dispatcher.add_handler(InlineQueryHandler(inline_caps))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('start',start))

    updater.start_polling()
    updater.idle()