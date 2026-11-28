import hashlib
import uuid
from pathlib import PurePath

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiTypes, extend_schema

from apps.portal.permissions import audit, require
from .models import TicketAttachment
from .services import visible_tickets

TYPES = {'.pdf': 'application/pdf', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}


@extend_schema(request=OpenApiTypes.OBJECT, responses=OpenApiTypes.OBJECT)
class AttachmentView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, pk):
        ticket = get_object_or_404(visible_tickets(request.user), pk=pk)
        require(request.user, 'ticket.reply', ticket.department_id)
        if ticket.status in ('closed', 'resolved'):
            raise ValidationError('ابتدا درخواست را بازگشایی کنید.')
        upload = request.FILES.get('file')
        if not upload or upload.size == 0 or upload.size > 10 * 1024 * 1024:
            raise ValidationError('حجم فایل باید بین یک بایت و ۱۰ مگابایت باشد.')
        suffix = PurePath(upload.name).suffix.lower()
        mime = TYPES.get(suffix)
        prefix = upload.read(16)
        valid = (suffix == '.pdf' and prefix.startswith(b'%PDF-') or suffix == '.png' and prefix.startswith(b'\x89PNG\r\n\x1a\n') or suffix in ('.jpg', '.jpeg') and prefix.startswith(b'\xff\xd8\xff') or suffix == '.webp' and prefix[:4] == b'RIFF' and prefix[8:12] == b'WEBP')
        if not mime or upload.content_type != mime or not valid:
            raise ValidationError('نوع، پسوند یا محتوای فایل مجاز نیست. PDF، PNG، JPG یا WebP انتخاب کنید.')
        upload.seek(0)
        digest = hashlib.sha256()
        for chunk in upload.chunks():
            digest.update(chunk)
        upload.seek(0)
        original = upload.name.replace('\\', '/').rsplit('/', 1)[-1]
        original = ''.join(c for c in original if c.isprintable())[:160] or 'attachment' + suffix
        upload.name = uuid.uuid4().hex + suffix
        attachment = TicketAttachment.objects.create(ticket=ticket, uploaded_by=request.user, file=upload, original_name=original, size=upload.size, content_type=mime, sha256=digest.hexdigest())
        audit(request.user, 'attachment.upload', attachment.pk, ticket.department)
        return Response({'id': attachment.pk, 'name': original, 'size': attachment.size}, status=201)

    def get(self, request, pk, attachment_id):
        ticket = get_object_or_404(visible_tickets(request.user), pk=pk)
        attachment = get_object_or_404(TicketAttachment, pk=attachment_id, ticket=ticket)
        audit(request.user, 'attachment.download', attachment.pk, ticket.department)
        response = FileResponse(attachment.file.open('rb'), as_attachment=True, filename=attachment.original_name, content_type=attachment.content_type)
        response['X-Content-Type-Options'] = 'nosniff'
        return response
