from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50  # default number of items per page
    page_size_query_param = 'page_size'  # allow client to override page size
    max_page_size = 200  # maximum items per page
