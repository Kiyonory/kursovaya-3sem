import django_filters
from .models import Service, Request


class ServiceFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Название')
    category = django_filters.NumberFilter(field_name='category_id', label='ID категории')
    category_name = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains', label='Название категории')
    duration_min = django_filters.NumberFilter(field_name='duration_days', lookup_expr='gte', label='Мин. срок (дней)')
    duration_max = django_filters.NumberFilter(field_name='duration_days', lookup_expr='lte', label='Макс. срок (дней)')

    class Meta:
        model = Service
        fields = ['name', 'category', 'category_name', 'duration_min', 'duration_max']


class RequestFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=Request.STATUS_CHOICES, label='Статус')
    user = django_filters.NumberFilter(field_name='user_id', label='ID пользователя')
    service = django_filters.NumberFilter(field_name='service_id', label='ID услуги')
    service_name = django_filters.CharFilter(field_name='service__name', lookup_expr='icontains', label='Название услуги')
    office = django_filters.NumberFilter(field_name='office_id', label='ID отделения')
    office_address = django_filters.CharFilter(field_name='office__address', lookup_expr='icontains', label='Адрес отделения')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte', label='Создана после')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte', label='Создана до')

    class Meta:
        model = Request
        fields = ['status', 'user', 'service', 'service_name', 'office', 'office_address', 'created_after', 'created_before']
