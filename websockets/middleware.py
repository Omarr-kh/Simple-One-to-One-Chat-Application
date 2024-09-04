from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser


@database_sync_to_async
def get_user_by_token(token_key):
    try:
        return Token.objects.get(key=token_key).user
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = dict(scope["headers"])
        if b"authorization" in headers:
            try:
                name, key = headers[b"authorization"].decode().split()
                if name.lower() == "token":
                    user = await get_user_by_token(key)
                    scope["user"] = user
            except Token.DoesNotExist:
                pass
        return await super().__call__(scope, receive, send)
