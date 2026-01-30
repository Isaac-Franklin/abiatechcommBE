from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()

class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware to authenticate WebSocket connections using JWT tokens
    """
    
    async def __call__(self, scope, receive, send):
        # Parse query string for token
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]
        
        # Try to authenticate user
        scope['user'] = await self.get_user_from_token(token)
        
        return await super().__call__(scope, receive, send)
    
    @database_sync_to_async
    def get_user_from_token(self, token):
        """
        Validate JWT token and return user
        """
        if not token:
            print("❌ No token provided")
            return AnonymousUser()
        
        try:
            # Decode and validate token
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            
            # Get user from database
            user = User.objects.get(id=user_id)
            print(f"✅ Authenticated user: {user.username} (ID: {user.id})")
            return user
            
        except TokenError as e:
            print(f"❌ Invalid token: {e}")
            return AnonymousUser()
        except User.DoesNotExist:
            print(f"❌ User not found for ID: {user_id}")
            return AnonymousUser()
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return AnonymousUser()