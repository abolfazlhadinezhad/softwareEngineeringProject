import logging
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is not None:
        details = response.data
        response.data = {'error': {'status': response.status_code, 'details': details}}
    if response is None:
        logging.getLogger(__name__).exception('Unhandled API exception')
        return Response({'error': {'status': 500, 'details': {'detail': 'An unexpected error occurred.'}}}, status=500)
    return response


def csrf_failure(request, reason=''):
    return JsonResponse({'error': {'status': 403, 'details': {'detail': 'CSRF verification failed. Refresh and try again.'}}}, status=403)
