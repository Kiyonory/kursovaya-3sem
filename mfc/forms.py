from django import forms
from django.core.exceptions import ValidationError
from .models import Service


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'category', 'duration_days']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название услуги (минимум 3 символа)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Введите описание услуги'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'duration_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 365
            }),
        }
        labels = {
            'name': 'Название услуги',
            'description': 'Описание',
            'category': 'Категория',
            'duration_days': 'Срок выполнения (дней)',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and len(name.strip()) < 3:
            raise ValidationError(
                'Название услуги должно содержать минимум 3 символа'
            )
        return name.strip() if name else name

    def clean_duration_days(self):
        duration_days = self.cleaned_data.get('duration_days')
        if duration_days and duration_days > 365:
            raise ValidationError(
                'Срок выполнения не может превышать 365 дней'
            )
        return duration_days
