# pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class that uses 'page' and 'limit' query params
    """
    page_size = 10  # Default page size
    page_size_query_param = 'limit'  # Allow client to set page size using ?limit=20
    page_query_param = 'page'  # Use ?page=2 for pagination
    max_page_size = 100  # Maximum limit allowed
    
    def get_paginated_response(self, data):
        """
        Custom paginated response format
        """
        return Response({
            'success': True,
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page.paginator.per_page,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
