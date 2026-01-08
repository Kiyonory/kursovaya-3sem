from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    User, Role, UserRole, ServiceCategory, Service,
    MFCOffice, Appointment, Request, Document
)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Административная панель для ролей"""
    list_display = ['id', 'name', 'users_count']
    list_display_links = ['id', 'name']
    search_fields = ['name']
    readonly_fields = ['id']

    @admin.display(description='Количество пользователей')
    def users_count(self, obj):
        """Количество пользователей с данной ролью"""
        count = obj.users.count()
        return count

    users_count.short_description = 'Количество пользователей'


class UserRoleInline(admin.TabularInline):
    """Inline для ролей пользователя"""
    model = UserRole
    extra = 1
    raw_id_fields = ['role']
    readonly_fields = ['assigned_at']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Административная панель для пользователей"""
    list_display = ['id', 'full_name', 'email', 'phone', 'roles_display', 'created_at', 'updated_at']
    list_display_links = ['id', 'full_name']
    list_filter = ['created_at']
    search_fields = ['full_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'id']
    date_hierarchy = 'created_at'
    inlines = [UserRoleInline]

    @admin.display(description='Роли')
    def roles_display(self, obj):
        """Отображение ролей пользователя"""
        roles = obj.roles.all()
        if roles:
            return ', '.join([role.name for role in roles])
        return 'Нет ролей'

    roles_display.short_description = 'Роли'


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Административная панель для связи пользователей и ролей"""
    list_display = ['id', 'user_link', 'role_link', 'assigned_at']
    list_display_links = ['id']
    list_filter = ['role', 'assigned_at']
    search_fields = ['user__full_name', 'user__email', 'role__name']
    raw_id_fields = ['user', 'role']
    readonly_fields = ['assigned_at', 'id']
    date_hierarchy = 'assigned_at'

    @admin.display(description='Пользователь')
    def user_link(self, obj):
        """Ссылка на пользователя"""
        url = reverse('admin:mfc_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.full_name)

    user_link.short_description = 'Пользователь'

    @admin.display(description='Роль')
    def role_link(self, obj):
        """Ссылка на роль"""
        url = reverse('admin:mfc_role_change', args=[obj.role.pk])
        return format_html('<a href="{}">{}</a>', url, obj.role.name)

    role_link.short_description = 'Роль'


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    """Административная панель для категорий услуг"""
    list_display = ['id', 'name', 'services_count', 'description_short']
    list_display_links = ['id', 'name']
    search_fields = ['name', 'description']
    readonly_fields = ['id']

    @admin.display(description='Количество услуг')
    def services_count(self, obj):
        """Количество услуг в категории"""
        count = obj.services.count()
        return count

    services_count.short_description = 'Количество услуг'

    @admin.display(description='Описание')
    def description_short(self, obj):
        """Краткое описание"""
        if obj.description:
            return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
        return '-'

    description_short.short_description = 'Описание'


class ServiceInline(admin.TabularInline):
    """Inline для услуг в категории"""
    model = Service
    extra = 1
    raw_id_fields = ['category']
    fields = ['name', 'duration_days']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Административная панель для услуг"""
    list_display = ['id', 'name', 'category_link', 'duration_days', 'description_short']
    list_display_links = ['id', 'name']
    list_filter = ['category', 'duration_days']
    search_fields = ['name', 'description', 'category__name']
    raw_id_fields = ['category']
    readonly_fields = ['id']

    @admin.display(description='Категория')
    def category_link(self, obj):
        """Ссылка на категорию"""
        url = reverse('admin:mfc_servicecategory_change', args=[obj.category.pk])
        return format_html('<a href="{}">{}</a>', url, obj.category.name)

    category_link.short_description = 'Категория'

    @admin.display(description='Описание')
    def description_short(self, obj):
        """Краткое описание"""
        if obj.description:
            return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
        return '-'

    description_short.short_description = 'Описание'


@admin.register(MFCOffice)
class MFCOfficeAdmin(admin.ModelAdmin):
    """Административная панель для отделений МФЦ"""
    list_display = ['id', 'address', 'district', 'working_hours', 'appointments_count']
    list_display_links = ['id', 'address']
    list_filter = ['district']
    search_fields = ['address', 'district', 'working_hours']

    @admin.display(description='Количество записей')
    def appointments_count(self, obj):
        """Количество записей в отделении"""
        count = obj.appointments.count()
        return count

    appointments_count.short_description = 'Количество записей'


class AppointmentInline(admin.TabularInline):
    """Inline для записей в отделении"""
    model = Appointment
    extra = 0
    raw_id_fields = ['user', 'service']
    readonly_fields = ['created_at']
    fields = ['user', 'service', 'appointment_datetime', 'status', 'created_at']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Административная панель для записей на приём"""
    list_display = [
        'id', 'user_link', 'service_link', 'office_link',
        'appointment_datetime', 'status_display', 'created_at'
    ]
    list_display_links = ['id']
    list_filter = ['status', 'appointment_datetime', 'created_at', 'office']
    search_fields = ['user__full_name', 'user__email', 'service__name', 'office__address']
    raw_id_fields = ['user', 'service', 'office']
    readonly_fields = ['created_at', 'id']
    date_hierarchy = 'appointment_datetime'

    @admin.display(description='Пользователь')
    def user_link(self, obj):
        """Ссылка на пользователя"""
        url = reverse('admin:mfc_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.full_name)

    user_link.short_description = 'Пользователь'

    @admin.display(description='Услуга')
    def service_link(self, obj):
        """Ссылка на услугу"""
        url = reverse('admin:mfc_service_change', args=[obj.service.pk])
        return format_html('<a href="{}">{}</a>', url, obj.service.name)

    service_link.short_description = 'Услуга'

    @admin.display(description='Отделение')
    def office_link(self, obj):
        """Ссылка на отделение"""
        url = reverse('admin:mfc_mfcoffice_change', args=[obj.office.pk])
        return format_html('<a href="{}">{}</a>', url, obj.office.address)

    office_link.short_description = 'Отделение'

    @admin.display(description='Статус')
    def status_display(self, obj):
        """Отображение статуса с цветом"""
        colors = {
            'pending': 'orange',
            'confirmed': 'green',
            'completed': 'blue',
            'cancelled': 'red',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )

    status_display.short_description = 'Статус'


class DocumentInline(admin.TabularInline):
    """Inline для документов в заявке"""
    model = Document
    extra = 1
    raw_id_fields = ['uploaded_by']
    readonly_fields = ['uploaded_at']
    fields = ['file', 'file_type', 'uploaded_by', 'uploaded_at']


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    """Административная панель для заявок"""
    list_display = [
        'id', 'user_link', 'service_link', 'status_display',
        'created_at', 'updated_at', 'documents_count'
    ]
    list_display_links = ['id']
    list_filter = ['status', 'created_at', 'updated_at', 'service']
    search_fields = ['user__full_name', 'user__email', 'service__name']
    raw_id_fields = ['user', 'service']
    readonly_fields = ['created_at', 'updated_at', 'id']
    date_hierarchy = 'created_at'
    inlines = [DocumentInline]

    @admin.display(description='Пользователь')
    def user_link(self, obj):
        """Ссылка на пользователя"""
        url = reverse('admin:mfc_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.full_name)

    user_link.short_description = 'Пользователь'

    @admin.display(description='Услуга')
    def service_link(self, obj):
        """Ссылка на услугу"""
        url = reverse('admin:mfc_service_change', args=[obj.service.pk])
        return format_html('<a href="{}">{}</a>', url, obj.service.name)

    service_link.short_description = 'Услуга'

    @admin.display(description='Статус')
    def status_display(self, obj):
        """Отображение статуса с цветом"""
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

    status_display.short_description = 'Статус'

    @admin.display(description='Количество документов')
    def documents_count(self, obj):
        """Количество документов в заявке"""
        count = obj.documents.count()
        return count

    documents_count.short_description = 'Документов'


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Административная панель для документов"""
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
        """Ссылка на заявку"""
        url = reverse('admin:mfc_request_change', args=[obj.request.pk])
        return format_html('<a href="{}">Заявка #{}</a>', url, obj.request.id)

    request_link.short_description = 'Заявка'

    @admin.display(description='Имя файла')
    def file_name(self, obj):
        """Имя файла"""
        return obj.file.name.split('/')[-1]

    file_name.short_description = 'Имя файла'

    @admin.display(description='Загрузил')
    def uploaded_by_link(self, obj):
        """Ссылка на пользователя, загрузившего документ"""
        if obj.uploaded_by:
            url = reverse('admin:mfc_user_change', args=[obj.uploaded_by.pk])
            return format_html('<a href="{}">{}</a>', url, obj.uploaded_by.full_name)
        return '-'

    uploaded_by_link.short_description = 'Загрузил'
