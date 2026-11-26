import django_filters
from .models import Ticket


class TicketFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name='category_id')

    class Meta:
        model = Ticket
        fields = ['status', 'priority', 'category']
