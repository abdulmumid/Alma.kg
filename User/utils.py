from onesignal_sdk.client import Client
from django.conf import settings

def send_push_notification(user, message):
    if not getattr(user, "player_id", None):
        return False

    client = Client(app_id=settings.ONESIGNAL_APP_ID, rest_api_key=settings.ONESIGNAL_API_KEY)

    notification_data = {
        "contents": {"en": message},
        "include_player_ids": [user.player_id]
    }

    try:
        response = client.send_notification(notification_data)
        return response
    except Exception as e:
        print(f"Ошибка при отправке пуша: {e}")
        return False
