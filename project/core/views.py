from django.shortcuts import render
from django.views.generic import TemplateView


class MainView(TemplateView):
    """
    Основное представление для отображения главной страницы
    """
    template_name = 'base_page.html'
