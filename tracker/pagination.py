# api/pagination.py
from rest_framework.pagination import LimitOffsetPagination

class StandardResultsSetPagination(LimitOffsetPagination):
    default_limit = 25
    max_limit = 100
