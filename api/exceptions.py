from rest_framework.views import exception_handler
from rest_framework.response import Response
import traceback

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # Log the traceback
    traceback.print_exc()

    # If response is None, it's an unhandled exception
    if response is None:
        return Response({
            "success": False,
            "message": str(exc)
        }, status=500)

    return response