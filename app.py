import logging
from credentials import TOKEN_BOT, REMBG_KEY
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from time import sleep
import requests
import os


logging.basicConfig(
    format='%(asctime)s-%(name)s-%(levelname)s-%(message)s',
    level=logging.INFO
)

# /start COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I'm bgRemoverBot  !",
        parse_mode='Markdown'
    )

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    sleep(1) # For wait 1000ms
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Give me an image and I'll clean up the background for you ! 🗨"
    )

# /help COMMAND
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="""
            How to use me ? 🤓 :
            1. Send me a photo you want to process.
            2. Recieve your Image without background, ready to use !
        """
    )

# /start of background extraction
async def cleanbg(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.photo:

        photo_id = update.message.photo[-1].file_id
        file = await context.bot.get_file(photo_id)
        fileDown_ = await file.download_to_drive()

        url = 'https://api.remove.bg/v1.0/removebg'
        files = {"image_file": open(fileDown_, 'rb')}
        data = {"size": "auto"}
        headers = {"X-Api-Key": REMBG_KEY}

        response_ = requests.post(url, files=files, data=data, headers=headers)
        if response_.status_code == 200:

            with open('Your-Image-no-bg.png', 'wb') as out:
                out.write(response_.content)

            with open('Your-Image-no-bg.png', 'rb') as no_bg:

                await context.bot.send_chat_action (
                    chat_id=update.effective_chat.id,
                    action="upload_document"
                )
                
                sleep(1)

                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=no_bg
                )

        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Error processing image..."
            )
        # Close file before removing
        if "image_file" in files:
            files["image_file"].close()

        # Deleting temporary files
        os.remove(fileDown_)
        os.remove('Your-Image-no-bg.png')

        await context.bot.send_chat_action (
            chat_id=update.effective_chat.id,
            action="typing"
        )

        sleep(0.5)

        await context.bot.send_message(
            chat_id=update.effective_chat. id,
            text="OK, now give me another images I'll clean up the background for you !"
        )
        
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry but is an image that is expected of you ! "
        )
        sleep(0.2) 
        await context.bot.send_message(
            chat_id=update.effective_chat. id,
            text="OK, now give me another images I'll clean up the background for you !"
        )


if __name__ == "__main__":

    rembgApp = ApplicationBuilder().token(TOKEN_BOT).build()

    startHandler_ = CommandHandler("start", start)
    helpHandler_ = CommandHandler("help", help)
    rembgHandler_ = MessageHandler(filters.ALL & (~filters.COMMAND), cleanbg)

    rembgApp.add_handler(rembgHandler_)
    rembgApp.add_handler(helpHandler_)
    rembgApp.add_handler(startHandler_)

    rembgApp.run_polling()