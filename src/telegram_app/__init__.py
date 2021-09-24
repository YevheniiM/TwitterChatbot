import telegram
from django.conf import settings

bot = telegram.Bot(settings.TELEGRAM_TOKEN)
