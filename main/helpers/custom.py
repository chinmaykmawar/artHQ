from django.http import JsonResponse

class CustomJsonResponse(JsonResponse):
    def __init__(self, data=None, status='success', error=None, **kwargs):
        response_data = {
            'status': status,
            'data': data,
            'error': error
        }
        super().__init__(response_data, **kwargs)