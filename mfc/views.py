from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Service
from .forms import ServiceForm


class ServiceListView(ListView):
    model = Service
    template_name = 'mfc/service_list.html'
    context_object_name = 'services'
    paginate_by = 10

    def get_queryset(self):
        queryset = Service.objects.select_related('category').prefetch_related('requests').all()

        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        category_id = self.request.GET.get('category', '')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        duration_max = self.request.GET.get('duration_max', '')
        if duration_max:
            try:
                queryset = queryset.filter(duration_days__lte=int(duration_max))
            except ValueError:
                pass

        short_duration = self.request.GET.get('short_duration', '')
        popular = self.request.GET.get('popular', '')

        if short_duration == 'on' and popular != 'on':
            queryset = queryset.filter(duration_days__lte=7)
        elif popular == 'on' and short_duration != 'on':
            queryset = queryset.filter(requests__isnull=False).distinct()
        elif short_duration == 'on' and popular == 'on':
            q_objects = Q(duration_days__lte=7) | Q(requests__isnull=False)
            queryset = queryset.filter(q_objects).distinct()

        complex_filter2 = self.request.GET.get('complex_filter2', '')
        if complex_filter2 == 'on':
            q_complex2 = Q(duration_days__gt=7) & (
                Q(description__isnull=True) | Q(description='')
            )
            queryset = queryset.filter(q_complex2).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import ServiceCategory

        context['categories'] = ServiceCategory.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['duration_max'] = self.request.GET.get('duration_max', '')
        context['short_duration'] = self.request.GET.get('short_duration', '')
        context['popular'] = self.request.GET.get('popular', '')
        context['complex_filter2'] = self.request.GET.get('complex_filter2', '')

        query_dict = self.request.GET.copy()
        if 'page' in query_dict:
            del query_dict['page']
        context['query_string'] = query_dict.urlencode()

        return context


class ServiceDetailView(DetailView):
    model = Service
    template_name = 'mfc/service_detail.html'
    context_object_name = 'service'


class ServiceCreateView(CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'mfc/service_form.html'
    success_url = reverse_lazy('mfc:service_list')

    def form_valid(self, form):
        messages.success(self.request, 'Услуга успешно добавлена!')
        return super().form_valid(form)


class ServiceUpdateView(UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'mfc/service_form.html'
    success_url = reverse_lazy('mfc:service_list')

    def form_valid(self, form):
        messages.success(self.request, 'Услуга успешно обновлена!')
        return super().form_valid(form)


class ServiceDeleteView(DeleteView):
    model = Service
    template_name = 'mfc/service_confirm_delete.html'
    success_url = reverse_lazy('mfc:service_list')
    context_object_name = 'service'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Услуга успешно удалена!')
        return super().delete(request, *args, **kwargs)


def index(request):
    return render(request, 'mfc/index.html')
