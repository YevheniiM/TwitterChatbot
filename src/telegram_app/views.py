from django.http import JsonResponse
from telegram import Bot
from django.conf import settings


def get_channel_id(request):
    channel_username = request.GET.get('channel_username')

    if not channel_username:
        return JsonResponse({"error": "'channel_username' is required as query parameters."},
                            status=400)

    bot = Bot(token=settings.TELEGRAM_TOKEN)
    updates = bot.get_updates()

    for update in updates:
        if update.channel_post and update.channel_post.chat.username == channel_username:
            return JsonResponse({"channel_id": update.channel_post.chat.id})

    return JsonResponse({"error": "Channel not found or no recent messages."}, status=404)
