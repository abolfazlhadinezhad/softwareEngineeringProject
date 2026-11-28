import uuid


class NoStoreMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.correlation_id = uuid.uuid4()
        response = self.get_response(request)
        response['X-Request-ID'] = str(request.correlation_id)
        if request.path.startswith('/api/'):
            response['Cache-Control'] = 'no-store'
        return response
