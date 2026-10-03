import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.helpers import escape_markdown

# Retrieve token from environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Base URL of your hosted Flask API
API_BASE_URL = "https://ff-info-api-fixed.onrender.com"

# Set your Telegram Channel username (without @ symbol)
CHANNEL_USERNAME = "MAHIM_COMMUNITY"

# Setup logging configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)

# Function to check channel membership
async def is_user_subscribed(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ["creator", "administrator", "member"]
    except Exception:
        # Fallback to allow access if bot is not admin in channel
        return True

# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_first_name = update.effective_user.first_name or "User"
    safe_name = escape_markdown(user_first_name, version=2)

    # Check force channel join
    is_joined = await is_user_subscribed(user_id, context)
    if not is_joined:
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        join_msg = (
            f"🚫 *Access Denied\!\*\n\n"
            f"Welcome *{safe_name}*\! To use this bot, you must join our official channel first\. Click the button below to join\!"
        )
        await update.message.reply_text(join_msg, parse_mode="MarkdownV2", reply_markup=reply_markup)
        return

    welcome_text = (
        f"✨ *━━━━━━━━━━━━━━━━━━* ✨\n"
        f"👋 *WELCOME {safe_name}\!*\n"
        f"✨ *━━━━━━━━━━━━━━━━━━* ✨\n\n"
        f"🎮 *FREE FIRE INFO BOT*\n\n"
        f"⚙️ *How to Search Player Data:*\n"
        f"`/info <UID> <REGION>`\n\n"
        f"💡 *Example:*\n"
        f"`/info 8180094463 sg`\n\n"
        f"━━━━━━━ ✦ ━━━━━━━"
    )
    await update.message.reply_text(welcome_text, parse_mode="MarkdownV2")

# Command handler for /info
async def get_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Check force channel join
    is_joined = await is_user_subscribed(user_id, context)
    if not is_joined:
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        join_msg = (
            f"🚫 *Access Denied\!\*\n\n"
            f"To use this bot, you must join our official channel first\! Click the button below to join\."
        )
        await update.message.reply_text(join_msg, parse_mode="MarkdownV2", reply_markup=reply_markup)
        return

    # Validate command arguments
    if len(context.args) < 2:
        error_msg = (
            "⚠️ *Invalid Command Format\!\n\n*"
            "👉 *Usage:* `/info <UID> <REGION>`\n"
            "💡 *Example:* `/info 8180094463 sg`"
        )
        await update.message.reply_text(error_msg, parse_mode="MarkdownV2")
        return

    uid = context.args[0]
    region = context.args[1].lower()

    loading_msg = await update.message.reply_text("🔄 _Fetching player details from server\.\.\._", parse_mode="MarkdownV2")

    try:
        response = requests.get(
            f"{API_BASE_URL}/info", 
            params={"uid": uid, "region": region}, 
            timeout=12
        )
        
        if response.status_code == 200:
            data = response.json()
            
            account_name = str(data.get("AccountName", "N/A"))
            account_level = str(data.get("AccountLevel", "N/A"))
            likes = str(data.get("Likes", "N/A"))
            
            safe_acc_name = escape_markdown(account_name, version=2)
            safe_uid = escape_markdown(uid, version=2)
            safe_level = escape_markdown(account_level, version=2)
            safe_likes = escape_markdown(likes, version=2)
            safe_region = escape_markdown(region.upper(), version=2)

            card_response = (
                f"🎮 *━━━━━━━━━━━━━━━━━━* 🎮\n"
                f"🔥 *PLAYER PROFILE DATA* 🔥\n"
                f"🎮 *━━━━━━━━━━━━━━━━━━* 🎮\n\n"
                f"👤 *Name:* `{safe_acc_name}`\n"
                f"🆔 *UID:* `{safe_uid}`\n"
                f"⭐ *Level:* *{safe_level}*\n"
                f"👍 *Likes:* *{safe_likes}*\n"
                f"🌐 *Region:* *{safe_region}*\n\n"
                f"⚡ _Powered by Free Fire Info Bot_\n"
                f"━━━━━━━ ✦ ━━━━━━━"
            )
            await loading_msg.edit_text(card_response, parse_mode="MarkdownV2")
        else:
            await loading_msg.edit_text("❌ *Player Not Found\!\n\nPlease check UID and Region\.*", parse_mode="MarkdownV2")

    except Exception:
        await loading_msg.edit_text("⚠️ *Server Error\!\n\nUnable to reach API server\.*", parse_mode="MarkdownV2")

def main():
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN environment variable not set!")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", get_info))

    print("Bot is running 24/7...")
    app.run_polling()

if __name__ == "__main__":
    main()
