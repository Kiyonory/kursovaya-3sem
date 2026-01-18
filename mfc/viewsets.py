from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Service, Request
from .serializers import ServiceSerializer, RequestSerializer
from .filters import ServiceFilter, RequestFilter


class ServiceViewSet(viewsets.ModelViewSet):
    """ViewSet для услуг МФЦ"""
    queryset = Service.objects.select_related('category').all()  # type: ignore
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ServiceFilter
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'duration_days', 'category__name']
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()

        short_duration = self.request.query_params.get('short_duration', None)
        popular = self.request.query_params.get('popular', None)

        if short_duration == 'true' or popular == 'true':
            q_objects = Q()

            if short_duration == 'true':
                q_objects |= Q(duration_days__lte=7)

            if popular == 'true':
                q_objects |= Q(requests__isnull=False)

            queryset = queryset.filter(q_objects).distinct()

        complex_filter = self.request.query_params.get('complex_filter', None)
        if complex_filter == 'true':
            q_complex = ~Q(duration_days__lte=7) & (
                Q(requests__isnull=False) | Q(description__isnull=False)
            )
            queryset = queryset.filter(q_complex).distinct()

        return queryset

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Статистика по услугам"""
        total_services = Service.objects.count()  # type: ignore
        services_by_category = Service.objects.values('category__name').annotate(  # type: ignore
            count=Count('id')
        )
        avg_duration = Service.objects.aggregate(  # type: ignore
            avg_duration=Avg('duration_days')
        )

        return Response({
            'total_services': total_services,
            'services_by_category': list(services_by_category),
            'average_duration_days': round(avg_duration['avg_duration'] or 0, 2)
        })

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Дублирование услуги"""
        service = self.get_object()
        new_service = Service.objects.create(
            name=f"{service.name} (копия)",
            description=service.description,
            category=service.category,
            duration_days=service.duration_days
        )
        serializer = self.get_serializer(new_service)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RequestViewSet(viewsets.ModelViewSet):
    """ViewSet для заявок"""
    queryset = Request.objects.select_related('user', 'service', 'office').all()  # type: ignore
    serializer_class = RequestSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RequestFilter
    search_fields = ['service__name', 'user__full_name', 'status']
    ordering_fields = ['created_at', 'updated_at', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_authenticated:
            if not self.request.user.is_staff:
                queryset = queryset.filter(user__email=self.request.user.email)

        status_filter = self.request.query_params.get('active_status', None)
        if status_filter == 'true':
            queryset = queryset.filter(
                Q(status='in_progress') | Q(status='new')
            )

        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)

        if date_from or date_to:
            q_date = Q()
            if date_from:
                q_date &= Q(created_at__gte=date_from)
            if date_to:
                q_date &= Q(created_at__lte=date_to)
            queryset = queryset.filter(q_date)

        complex_filter = self.request.query_params.get('complex_filter', None)
        if complex_filter == 'true' and self.request.user.is_authenticated:
            user_email = self.request.user.email
            q_complex = ~Q(user__email=user_email) & (
                Q(status='in_progress') | Q(status='new')
            )
            queryset = queryset.filter(q_complex).distinct()

        return queryset

    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Получить заявки текущего пользователя"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Требуется аутентификация'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user_email = request.user.email
        requests = Request.objects.filter(  # type: ignore
            Q(user__email=user_email)
        ).select_related('user', 'service')

        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Изменить статус заявки"""
        request_obj = self.get_object()
        new_status = request.data.get('status')

        if not new_status:
            return Response(
                {'error': 'Не указан статус'},
                status=status.HTTP_400_BAD_REQUEST
            )

        valid_statuses = ['new', 'in_progress', 'completed', 'rejected']
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Неверный статус. Допустимые: {", ".join(valid_statuses)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        request_obj.status = new_status
        request_obj.save()

        serializer = self.get_serializer(request_obj)
        return Response(serializer.data)
