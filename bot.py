import logging
import psycopg2
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    Application
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Veritabanı Bilgileri
DB_NAME = "postgres"
DB_USER = "botuser"
DB_PASSWORD = "admin"
DB_HOST = "localhost"
DB_PORT = "5432"

ADMIN_CHAT_ID = 649226694  # Kendi chat_id'niz

# --------------------------------------------------------------
# Veritabanı Fonksiyonları
# --------------------------------------------------------------
def ensure_user_in_db(chat_id: int):
    """Kullanıcı bot_users tablosunda yoksa ekle."""
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
            cur.execute("INSERT INTO bot_users (chat_id) VALUES (%s)", (chat_id,))
            conn.commit()
    except Exception as e:
        logging.error(f"ensure_user_in_db hatası: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def is_user_authorized(chat_id: int) -> bool:
    """Kullanıcının is_authorized olup olmadığını döndür."""
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
        logging.error(f"is_user_authorized hatası: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
    return authorized

def authorize_user_in_db(chat_id: int):
    """Kullanıcıyı is_authorized=true yap."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        cur.execute("UPDATE bot_users SET is_authorized = true WHERE chat_id = %s", (chat_id,))
        conn.commit()
    except Exception as e:
        logging.error(f"authorize_user_in_db hatası: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def search_in_leaks(keyword: str):
    """Tek sütun (data) içinde %keyword% arar, sonuçları listede döndür."""
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
        logging.error(f"search_in_leaks hatası: {e}")
        results = None  # Hata durumunu belirtmek için None
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
    return results

# --------------------------------------------------------------
# Bot Komut Fonksiyonları (ASYNC!)
# --------------------------------------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    ensure_user_in_db(chat_id)
    text = (
        "Merhaba, ben sızıntı verileri arama aracıyım...\n"
        "Komutlar için /help yazabilirsiniz."
    )
    # ASYNC fonksiyonda reply_text bir coroutine -> await
    await update.message.reply_text(text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Komutlar:\n"
        "/start - Botu başlat\n"
        "/help - Yardım\n"
        "/authorize <chat_id> - Kullanıcı yetkilendirme.\n"
        "/search <keyword> - Sızıntı arama\n"
    )
    await update.message.reply_text(text)

async def authorize_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    requester_id = update.effective_user.id
    if requester_id != ADMIN_CHAT_ID:
        await update.message.reply_text("Bu komutu kullanamazsın.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Kullanıcı chat_id girin. Örnek: /authorize 123456789")
        return

    try:
        target_chat_id = int(context.args[0])
        authorize_user_in_db(target_chat_id)
        await update.message.reply_text(f"Kullanıcı {target_chat_id} yetkilendirildi.")
    except ValueError:
        await update.message.reply_text("Geçerli bir sayı formatında chat_id giriniz.")

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    if not is_user_authorized(chat_id):
        await update.message.reply_text("Arama yetkiniz yok.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("Aramak istediğiniz kelimeyi girin. Örnek: /search [sızıntı_ismi]")
        return

    keyword = " ".join(context.args)
    data_list = search_in_leaks(keyword)
    if data_list is None:
        await update.message.reply_text("Hata oluştu. Lütfen tekrar deneyin.")
        return
    if len(data_list) == 0:
        await update.message.reply_text("Hiç sonuç bulunamadı.")
        return

    output_file = "results.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        for line in data_list:
            f.write(line + "\n")

    await update.message.reply_document(document=open(output_file, "rb"))

# --------------------------------------------------------------
# Ana Uygulama (senkron run_polling, async komutlar)
# --------------------------------------------------------------
def main():
    from telegram.ext import ApplicationBuilder

    TOKEN = ""

    # ApplicationBuilder ile bir Application oluşturuyoruz.
    app = ApplicationBuilder().token(TOKEN).build()

    # Komutları kaydet
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("authorize", authorize_command))
    app.add_handler(CommandHandler("search", search_command))

    print("Bot çalışıyor...")
    # Bu metot bloklayıcıdır (SENKRON). Kendi içinde event loop yönetir.
    app.run_polling()

if __name__ == "__main__":
    main()
