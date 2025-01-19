import os
import logging
import psycopg2
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Fetch environment variables directly
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
TOKEN = os.getenv("TOKEN")

# Validate critical environment variables
if not TOKEN:
    raise EnvironmentError("Missing TOKEN environment variable.")
if not DB_NAME or not DB_USER or not DB_PASSWORD or not DB_HOST or not DB_PORT:
    raise EnvironmentError("Database configuration is incomplete. Check environment variables.")

# --------------------------------------------------------------
# Database Functions
# --------------------------------------------------------------
def ensure_user_in_db(chat_id: int):
    """Ensure the user exists in bot_users table."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        cur.execute("SELECT chat_id FROM bot_users WHERE chat_id = %s", (chat_id,))
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO bot_users (chat_id, is_authorized) VALUES (%s, FALSE)", (chat_id,))
            conn.commit()
    except Exception as e:
        logging.error(f"ensure_user_in_db error: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def is_user_authorized(chat_id: int) -> bool:
    """Check if the user is authorized."""
    authorized = False
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        cur.execute("SELECT is_authorized FROM bot_users WHERE chat_id = %s", (chat_id,))
        row = cur.fetchone()
        if row:
            authorized = row[0]
    except Exception as e:
        logging.error(f"is_user_authorized error: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
    return authorized

def authorize_user_in_db(chat_id: int):
    """Authorize the user by setting is_authorized=True."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        cur.execute("UPDATE bot_users SET is_authorized = TRUE WHERE chat_id = %s", (chat_id,))
        conn.commit()
    except Exception as e:
        logging.error(f"authorize_user_in_db error: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def get_admin_chat_id() -> list[int]:
    """Fetch a list of admin chat IDs from the bot_users table."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        cur.execute("SELECT chat_id FROM bot_users WHERE is_authorized = TRUE")
        rows = cur.fetchall()
        admin_chat_ids = [row[0] for row in rows]
        if not admin_chat_ids:
            raise ValueError("No admin users found in the bot_users table.")
        return admin_chat_ids
    except Exception as e:
        logging.error(f"get_admin_chat_id error: {e}")
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def search_in_leaks(keyword: str):
    """Search for the keyword in the leaks table."""
    results = []
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        query = "SELECT data FROM leaks WHERE data ILIKE %s"
        like_pattern = f"%{keyword}%"
        cur.execute(query, (like_pattern,))
        rows = cur.fetchall()
        results = [row[0] for row in rows]
    except Exception as e:
        logging.error(f"search_in_leaks error: {e}")
        results = None  # Indicate an error occurred
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
    return results

# --------------------------------------------------------------
# Bot Command Functions (ASYNC)
# --------------------------------------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    ensure_user_in_db(chat_id)
    text = (
        "Hello, I am your leak data search assistant...\n"
        "Type /help to see available commands."
    )
    await update.message.reply_text(text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Display help\n"
        "/authorize <chat_id> - Authorize a user\n"
        "/search <keyword> - Search leaks\n"
    )
    await update.message.reply_text(text)

async def authorize_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        admin_chat_ids = get_admin_chat_id()
    except Exception as e:
        await update.message.reply_text("Could not determine admins. Check logs for details.")
        return

    requester_id = update.effective_user.id
    if requester_id not in admin_chat_ids:
        await update.message.reply_text("You do not have permission to use this command.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Please provide a chat_id. Example: /authorize 123456789")
        return

    try:
        target_chat_id = int(context.args[0])
        authorize_user_in_db(target_chat_id)
        await update.message.reply_text(f"User {target_chat_id} has been authorized.")
    except ValueError:
        await update.message.reply_text("Please provide a valid numeric chat_id.")

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    if not is_user_authorized(chat_id):
        await update.message.reply_text("You are not authorized to search.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("Please provide a keyword to search for. Example: /search [keyword]")
        return

    keyword = " ".join(context.args)
    data_list = search_in_leaks(keyword)
    if data_list is None:
        await update.message.reply_text("An error occurred. Please try again later.")
        return
    if len(data_list) == 0:
        await update.message.reply_text("No results found.")
        return

    # Create a file named after the search keyword
    output_file = f"{keyword.replace(' ', '_')}.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        for line in data_list:
            f.write(line + "\n")

    await update.message.reply_document(document=open(output_file, "rb"))

# --------------------------------------------------------------
# Main Application
# --------------------------------------------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Register commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("authorize", authorize_command))
    app.add_handler(CommandHandler("search", search_command))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
