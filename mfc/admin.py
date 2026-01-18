from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import (
    User, ServiceCategory, Service,
    MFCOffice, Request, Document
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'phone', 'role_display', 'created_at', 'updated_at']
    list_display_links = ['id', 'full_name']
    list_filter = ['role', 'created_at']
    search_fields = ['full_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'id']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Основная информация', {
            'fields': ('full_name', 'email', 'phone', 'role')
        }),
        ('Системная информация', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Роль')
    def role_display(self, obj):
        return obj.get_role_display()


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'services_count', 'description_short']
    list_display_links = ['id', 'name']
    search_fields = ['name', 'description']
    readonly_fields = ['id']

    @admin.display(description='Количество услуг')
    def services_count(self, obj):
        return obj.services.count()

    @admin.display(description='Описание')
    def description_short(self, obj):
        if obj.description:
            return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
        return '-'


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1
    raw_id_fields = ['category']
    fields = ['name', 'duration_days']


class ServiceResource(resources.ModelResource):
    category_name = resources.Field(attribute='category__name', column_name='Категория')
    duration_days_formatted = resources.Field(column_name='Срок выполнения')

    class Meta:
        model = Service
        fields = ('id', 'name', 'description', 'category_name', 'duration_days_formatted')
        export_order = ('id', 'name', 'category_name', 'duration_days_formatted', 'description')

    def get_export_queryset(self):
        return self._meta.model.objects.filter(  # type: ignore
            Q(duration_days__lte=7) | Q(requests__isnull=False)
        ).distinct()

    def dehydrate_duration_days_formatted(self, service):
        return f"{service.duration_days} дней"

    def dehydrate_category_name(self, service):
        if service.category:
            return f"Категория: {service.category.name}"
        return "Без категории"


@admin.register(Service)
class ServiceAdmin(ImportExportModelAdmin):
    resource_class = ServiceResource
    list_display = ['id', 'name', 'category_link', 'duration_days', 'offices_count', 'description_short']
    list_display_links = ['id', 'name']
    list_filter = ['category', 'duration_days']
    search_fields = ['name', 'description', 'category__name']
    raw_id_fields = ['category']
    readonly_fields = ['id']
    filter_horizontal = ['offices']

    @admin.display(description='Количество отделений')
    def offices_count(self, obj):
        return obj.offices.count()

    @admin.display(description='Категория')
    def category_link(self, obj):
        url = reverse('admin:mfc_servicecategory_change', args=[obj.category.pk])
        return format_html('<a href="{}">{}</a>', url, obj.category.name)

    @admin.display(description='Описание')
    def description_short(self, obj):
        if obj.description:
            return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
        return '-'


class RequestInline(admin.TabularInline):
    model = Request
    extra = 0
    raw_id_fields = ['user', 'service']
    readonly_fields = ['created_at', 'updated_at']
    fields = ['user', 'service', 'status', 'created_at']


@admin.register(MFCOffice)
class MFCOfficeAdmin(admin.ModelAdmin):
    list_display = ['id', 'address', 'district', 'working_hours', 'services_count', 'requests_count']
    list_display_links = ['id', 'address']
    list_filter = ['district']
    search_fields = ['address', 'district', 'working_hours']
    inlines = [RequestInline]

    @admin.display(description='Количество услуг')
    def services_count(self, obj):
        return obj.services.count()

    @admin.display(description='Количество заявок')
    def requests_count(self, obj):
        return obj.requests.count()


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1
    raw_id_fields = ['uploaded_by']
    readonly_fields = ['uploaded_at']
    fields = ['file', 'file_type', 'uploaded_by', 'uploaded_at']


class RequestResource(resources.ModelResource):
    class Meta:
        model = Request
        fields = ('id', 'user__full_name', 'user__email', 'service__name', 'office__address', 'status', 'created_at', 'updated_at')
        export_order = ('id', 'user__full_name', 'user__email', 'service__name', 'office__address', 'status', 'created_at', 'updated_at')


@admin.register(Request)
class RequestAdmin(ImportExportModelAdmin):
    resource_class = RequestResource
    list_display = [
        'id', 'user_link', 'service_link', 'office_link', 'status_display',
        'created_at', 'updated_at', 'documents_count'
    ]
    list_display_links = ['id']
    list_filter = ['status', 'created_at', 'updated_at', 'service', 'office']
    search_fields = ['user__full_name', 'user__email', 'service__name', 'office__address']
    raw_id_fields = ['user', 'service', 'office']
    readonly_fields = ['created_at', 'updated_at', 'id']
    date_hierarchy = 'created_at'
    inlines = [DocumentInline]

    @admin.display(description='Пользователь')
    def user_link(self, obj):
        url = reverse('admin:mfc_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.full_name)

    @admin.display(description='Услуга')
    def service_link(self, obj):
        url = reverse('admin:mfc_service_change', args=[obj.service.pk])
        return format_html('<a href="{}">{}</a>', url, obj.service.name)

    @admin.display(description='Отделение')
    def office_link(self, obj):
        if obj.office:
            url = reverse('admin:mfc_mfcoffice_change', args=[obj.office.pk])
            return format_html('<a href="{}">{}</a>', url, obj.office.address)
        return '-'

    @admin.display(description='Статус')
    def status_display(self, obj):
        colors = {
            'new': 'blue',
            'in_progress': 'orange',
            'completed': 'green',
            'rejected': 'red',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )

    @admin.display(description='Количество документов')
    def documents_count(self, obj):
        return obj.documents.count()


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'request_link', 'file_name', 'file_type',
        'uploaded_by_link', 'uploaded_at'
    ]
    list_display_links = ['id']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['request__id', 'file', 'uploaded_by__full_name']
    raw_id_fields = ['request', 'uploaded_by']
    readonly_fields = ['uploaded_at', 'id']
    date_hierarchy = 'uploaded_at'

    @admin.display(description='Заявка')
    def request_link(self, obj):
        url = reverse('admin:mfc_request_change', args=[obj.request.pk])
        return format_html('<a href="{}">Заявка #{}</a>', url, obj.request.id)

    @admin.display(description='Имя файла')
    def file_name(self, obj):
        return obj.file.name.split('/')[-1]

    @admin.display(description='Загрузил')
    def uploaded_by_link(self, obj):
        if obj.uploaded_by:
            url = reverse('admin:mfc_user_change', args=[obj.uploaded_by.pk])
            return format_html('<a href="{}">{}</a>', url, obj.uploaded_by.full_name)
        return '-'
