from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Service
from .forms import ServiceForm


class ServiceListView(ListView):
    """Просмотр списка услуг"""
    model = Service
    template_name = 'mfc/service_list.html'
    context_object_name = 'services'
    paginate_by = 10

    def get_queryset(self):
        queryset = Service.objects.select_related('category').all()
        # Поиск по названию
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        # Фильтр по категории
        category_id = self.request.GET.get('category', '')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import ServiceCategory
        context['categories'] = ServiceCategory.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        return context


class ServiceDetailView(DetailView):
    """Просмотр детальной информации об услуге"""
    model = Service
    template_name = 'mfc/service_detail.html'
    context_object_name = 'service'


class ServiceCreateView(CreateView):
    """Добавление новой услуги"""
    model = Service
    form_class = ServiceForm
    template_name = 'mfc/service_form.html'
    success_url = reverse_lazy('mfc:service_list')

    def form_valid(self, form):
        messages.success(self.request, 'Услуга успешно добавлена!')
        return super().form_valid(form)


class ServiceUpdateView(UpdateView):
    """Редактирование услуги"""
    model = Service
    form_class = ServiceForm
    template_name = 'mfc/service_form.html'
    success_url = reverse_lazy('mfc:service_list')

    def form_valid(self, form):
        messages.success(self.request, 'Услуга успешно обновлена!')
        return super().form_valid(form)


class ServiceDeleteView(DeleteView):
    """Удаление услуги"""
    model = Service
    template_name = 'mfc/service_confirm_delete.html'
    success_url = reverse_lazy('mfc:service_list')
    context_object_name = 'service'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Услуга успешно удалена!')
        return super().delete(request, *args, **kwargs)


def index(request):
    """Главная страница"""
    return render(request, 'mfc/index.html')
