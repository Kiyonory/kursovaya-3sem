from django.db import models
from django.core.validators import MinValueValidator
from simple_history.models import HistoricalRecords


class User(models.Model):
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('admin', 'Администратор'),
    ]

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
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='Роль'
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
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name

    @property
    def is_admin(self):
        return self.role == 'admin'


class ServiceCategory(models.Model):
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
        default=1  # type: ignore
    )
    offices = models.ManyToManyField(
        'MFCOffice',
        related_name='services',
        verbose_name='Отделения МФЦ',
        blank=True,
        help_text='Отделения, где предоставляется данная услуга'
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['name']

    def __str__(self):
        return self.name


class MFCOffice(models.Model):
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


class Request(models.Model):
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
    office = models.ForeignKey(
        MFCOffice,
        on_delete=models.CASCADE,
        verbose_name='Отделение МФЦ',
        related_name='requests',
        null=True,
        blank=True
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
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заявка #{self.id} - {self.user.full_name} ({self.service.name})'  # type: ignore


class Document(models.Model):
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
    file = models.ImageField(
        upload_to='documents/%Y/%m/%d/',
        verbose_name='Файл (изображение)',
        help_text='Загрузите изображение (JPG, PNG, GIF)'
    )
    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPE_CHOICES,
        default='image',
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
        return f'Документ для заявки #{self.request.id} - {self.file.name}'  # type: ignore
