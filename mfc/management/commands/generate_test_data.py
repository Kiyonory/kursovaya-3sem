from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from mfc.models import ServiceCategory, Service, User, Request


class Command(BaseCommand):
    help = 'Генерирует тестовые данные для проекта МФЦ'

    def add_arguments(self, parser):
        parser.add_argument(
            '--categories',
            type=int,
            default=5,
            help='Количество категорий для создания',
        )
        parser.add_argument(
            '--services',
            type=int,
            default=10,
            help='Количество услуг для создания',
        )
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Количество пользователей для создания',
        )

    def handle(self, *args, **options):
        self.stdout.write('Начинаю генерацию тестовых данных...')

        categories_count = options['categories']
        categories = []
        category_names = [
            'Документы и удостоверения',
            'Регистрация',
            'Недвижимость',
            'Социальные услуги',
            'Транспорт',
            'Бизнес',
            'Семейные вопросы',
            'Образование',
        ]

        for i in range(categories_count):
            name = category_names[i] if i < len(category_names) else f'Категория {i + 1}'
            category, created = ServiceCategory.objects.get_or_create(
                name=name,
                defaults={'description': f'Описание категории {name}'}
            )
            categories.append(category)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создана категория: {name}'))

        services_count = options['services']
        service_names = [
            'Выдача паспорта РФ',
            'Замена паспорта',
            'Регистрация по месту жительства',
            'Оформление детского пособия',
            'Регистрация ИП',
            'Регистрация транспортного средства',
            'Замена водительского удостоверения',
            'Оформление субсидий на ЖКУ',
            'Регистрация брака',
            'Запись ребёнка в детский сад',
        ]

        for i in range(services_count):
            name = service_names[i] if i < len(service_names) else f'Услуга {i + 1}'
            category = categories[i % len(categories)]
            service, created = Service.objects.get_or_create(
                name=name,
                defaults={
                    'category': category,
                    'description': f'Описание услуги {name}',
                    'duration_days': (i % 30) + 1,  # От 1 до 30 дней
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создана услуга: {name}'))

        users_count = options['users']
        for i in range(users_count):
            user, created = User.objects.get_or_create(
                email=f'user{i + 1}@example.com',
                defaults={
                    'full_name': f'Пользователь {i + 1}',
                    'phone': f'+7 900 {1000000 + i}',
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан пользователь: {user.full_name}'))

        users = list(User.objects.all())
        services = list(Service.objects.all())

        if users and services:
            statuses = ['new', 'in_progress', 'completed', 'rejected']
            for i in range(min(10, len(users) * 2)):
                user = users[i % len(users)]
                service = services[i % len(services)]
                status = statuses[i % len(statuses)]

                request, created = Request.objects.get_or_create(
                    user=user,
                    service=service,
                    defaults={
                        'status': status,
                        'created_at': timezone.now() - timedelta(days=i),
                    }
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Создана заявка #{request.id} для {user.full_name}'
                        )
                    )

        self.stdout.write(self.style.SUCCESS('\nГенерация тестовых данных завершена!'))
        self.stdout.write(f'Категорий: {ServiceCategory.objects.count()}')
        self.stdout.write(f'Услуг: {Service.objects.count()}')
        self.stdout.write(f'Пользователей: {User.objects.count()}')
        self.stdout.write(f'Заявок: {Request.objects.count()}')
