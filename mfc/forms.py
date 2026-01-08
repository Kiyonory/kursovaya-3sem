from django import forms
from .models import Service


class ServiceForm(forms.ModelForm):
    """Форма для создания и редактирования услуги"""
    
    class Meta:
        model = Service
        fields = ['name', 'description', 'category', 'duration_days']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название услуги'
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
                'min': 1
            }),
        }
        labels = {
            'name': 'Название услуги',
            'description': 'Описание',
            'category': 'Категория',
            'duration_days': 'Срок выполнения (дней)',
        }

