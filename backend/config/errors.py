from rest_framework.views import exception_handler as drf_exception_handler


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is not None:
        details = response.data
        response.data = {'error': {'status': response.status_code, 'details': details}}
    return response
