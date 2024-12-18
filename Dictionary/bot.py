import logging
import requests
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message when the /start command is issued."""
    update.message.reply_text('Hi! I can define words for you.')

def define_word(update: Update, context: CallbackContext) -> None:
    """Fetch the definition of a word from the dictionary API."""
    word = update.message.text
    print(f"Word received: {word}")
    
    response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')

    if response.status_code == 200:
        data = response.json()[0]
        word = data['word']
        phonetics_list = data['phonetics']
        meanings_list = data['meanings']
        source_list = data.get('sourceUrls', [])

        # Initialize empty lists for each phonetic type
        uk_phonetics = []
        us_phonetics = []
        au_phonetics = []

        # Separate the phonetics into their respective lists based on audio
        for phonetic in phonetics_list:
            audio = phonetic.get('audio', '')

            if 'uk' in audio.lower():
                uk_phonetics.append(f"UK: {audio}")
            elif 'us' in audio.lower():
                us_phonetics.append(f"US: {audio}")
            elif 'au' in audio.lower():
                au_phonetics.append(f"AU: {audio}")

        # Combine the phonetic lists into a single formatted string
        all_phonetics = []

        if uk_phonetics:
            all_phonetics.extend(uk_phonetics)
        if us_phonetics:
            all_phonetics.extend(us_phonetics)
        if au_phonetics:
            all_phonetics.extend(au_phonetics)

        # Create a final phonetics string with newline separators
        phonetics = '\n'.join(all_phonetics)

        # Format meanings
        meanings = '\n\n'.join(
            f"Part of Speech: {meaning['partOfSpeech']}\n"
            f"Definitions:\n{', '.join(definition['definition'] for definition in meaning['definitions'])}"
            for meaning in meanings_list
        )

        # Format source URLs
        source_urls = '\n'.join(source_list)

        # Prepare the final message with Markdown formatting
        message = (
            f"*Word:* {word}\n\n"  # Use asterisks for bold in Markdown
            f"*Phonetics:*\n{phonetics}\n\n"
            f"*Meanings:*\n{meanings}\n\n"
            f"*Source URLs:*\n{source_urls}"
        )
        # Send the message with Markdown parsing
        update.message.reply_text(message, parse_mode='Markdown')

    else:
        update.message.reply_text('Sorry, I could not find a definition for that word.')

def main() -> None:
    """Start the bot."""
    # Set up the Updater and Dispatcher
    updater = Updater(token=os.getenv('BOT_TOKEN'))
    dispatcher = updater.dispatcher

    # Add handlers for commands and messages
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, define_word))

    # Start polling for updates
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
