from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Role(models.Model):
    """Справочник ролей пользователей"""
    name = models.CharField(
        max_length=100,
        verbose_name='Название роли',
        unique=True
    )

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        ordering = ['name']

    def __str__(self):
        return self.name


class User(models.Model):
    """Пользователь системы"""
    full_name = models.CharField(
        max_length=200,
        verbose_name='ФИО'
    )
    email = models.EmailField(
        verbose_name='Email',
        unique=True
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    roles = models.ManyToManyField(
        Role,
        through='UserRole',
        related_name='users',
        verbose_name='Роли'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name


class UserRole(models.Model):
    """Связь многие-ко-многим между пользователями и ролями"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='user_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        verbose_name='Роль',
        related_name='user_roles'
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата назначения'
    )

    class Meta:
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'
        unique_together = ['user', 'role']
        ordering = ['-assigned_at']

    def __str__(self):
        return f'{self.user.full_name} - {self.role.name}'


class ServiceCategory(models.Model):
    """Справочник категорий услуг"""
    name = models.CharField(
        max_length=200,
        verbose_name='Название категории',
        unique=True
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Категория услуги'
        verbose_name_plural = 'Категории услуг'
        ordering = ['name']

    def __str__(self):
        return self.name


class Service(models.Model):
    """Услуга МФЦ"""
    name = models.CharField(
        max_length=200,
        verbose_name='Название услуги'
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True
    )
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        related_name='services'
    )
    duration_days = models.PositiveIntegerField(
        verbose_name='Срок выполнения (дней)',
        validators=[MinValueValidator(1)],
        default=1
    )

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['name']

    def __str__(self):
        return self.name


class MFCOffice(models.Model):
    """Отделение МФЦ"""
    address = models.CharField(
        max_length=500,
        verbose_name='Адрес'
    )
    district = models.CharField(
        max_length=200,
        verbose_name='Район',
        blank=True,
        null=True
    )
    working_hours = models.CharField(
        max_length=200,
        verbose_name='Режим работы',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Отделение МФЦ'
        verbose_name_plural = 'Отделения МФЦ'
        ordering = ['district', 'address']

    def __str__(self):
        return f'{self.district or ""} - {self.address}'.strip(' -')


class Appointment(models.Model):
    """Запись на приём"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('confirmed', 'Подтверждена'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='appointments'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        verbose_name='Услуга',
        related_name='appointments'
    )
    office = models.ForeignKey(
        MFCOffice,
        on_delete=models.CASCADE,
        verbose_name='Отделение',
        related_name='appointments'
    )
    appointment_datetime = models.DateTimeField(
        verbose_name='Дата и время приёма'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Запись на приём'
        verbose_name_plural = 'Записи на приём'
        ordering = ['-appointment_datetime']

    def __str__(self):
        return f'{self.user.full_name} - {self.service.name} ({self.appointment_datetime})'


class Request(models.Model):
    """Заявка на услугу"""
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В обработке'),
        ('completed', 'Завершена'),
        ('rejected', 'Отклонена'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='requests'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        verbose_name='Услуга',
        related_name='requests'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заявка #{self.id} - {self.user.full_name} ({self.service.name})'


class Document(models.Model):
    """Документ (работа с изображениями)"""
    FILE_TYPE_CHOICES = [
        ('image', 'Изображение'),
        ('pdf', 'PDF'),
        ('other', 'Другое'),
    ]

    request = models.ForeignKey(
        Request,
        on_delete=models.CASCADE,
        verbose_name='Заявка',
        related_name='documents'
    )
    file = models.FileField(
        upload_to='documents/%Y/%m/%d/',
        verbose_name='Файл'
    )
    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPE_CHOICES,
        default='other',
        verbose_name='Тип файла'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата загрузки'
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name='Загрузил',
        related_name='uploaded_documents',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'Документ для заявки #{self.request.id} - {self.file.name}'
