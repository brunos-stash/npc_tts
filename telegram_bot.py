from pathlib import Path
from telegram import Update, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultAudio
from telegram.ext import Updater, CommandHandler, CallbackContext, InlineQueryHandler

import tts

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
    
    results = list()
    # results.append(InlineQueryResultAudio(update.inline_query.query, ))
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title=query,
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)
    # file_path = tts.synthesize(update.inline_query.query)
    # update.message.reply_text('Done')
    # with open(file_path, 'rb') as f:
    #     _audio = f.read()
        # update.message.reply_audio(audio=_audio)

if __name__ == "__main__":
    with open('api.token', 'r') as f:
        token = f.readlines()
    updater = Updater(token[0])
    updater.dispatcher.add_handler(CommandHandler('tts', synthesize))
    updater.dispatcher.add_handler(InlineQueryHandler(inline_caps))

    updater.start_polling()
    updater.idle()