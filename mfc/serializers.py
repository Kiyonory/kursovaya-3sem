from rest_framework import serializers
from .models import Service, Request, ServiceCategory, User, MFCOffice


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'description']


class ServiceSerializer(serializers.ModelSerializer):
    category = ServiceCategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    def validate_duration_days(self, value):
        if value > 365:
            raise serializers.ValidationError(
                "Срок выполнения не может превышать 365 дней"
            )
        return value

    def validate_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Название услуги должно содержать минимум 3 символа"
            )
        return value.strip()

    class Meta:
        model = Service
        fields = [
            'id', 'name', 'description', 'category', 'category_id',
            'category_name', 'duration_days'
        ]
        extra_kwargs = {
            'name': {'required': True},
            'category_id': {'required': True},
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'phone', 'created_at']


class MFCOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MFCOffice
        fields = ['id', 'address', 'district', 'working_hours']


class RequestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    service = ServiceSerializer(read_only=True)
    service_id = serializers.IntegerField(write_only=True)
    office = MFCOfficeSerializer(read_only=True)
    office_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    def validate_status(self, value):
        valid_statuses = ['new', 'in_progress', 'completed', 'rejected']
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Статус должен быть одним из: {', '.join(valid_statuses)}"
            )
        return value

    class Meta:
        model = Request
        fields = [
            'id', 'user', 'user_id', 'service', 'service_id',
            'office', 'office_id', 'status', 'status_display', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'user_id': {'required': True},
            'service_id': {'required': True},
        }
