import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL")  # Render сам подставит domain
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH
