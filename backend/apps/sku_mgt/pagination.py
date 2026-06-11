from rest_framework.pagination import CursorPagination
from rest_framework.response import Response


class SkuCursorPagination(CursorPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 500
    ordering = "-id"

    def get_paginated_response(self, data):
        if isinstance(data, dict):
            code = data.get("code", 200)
            message = data.get("message", "success")
            results = data.get("data", [])
        else:
            code = 200
            message = "success"
            results = data

        return Response(
            {
                "code": code,
                "message": message,
                "data": results,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
            }
        )
