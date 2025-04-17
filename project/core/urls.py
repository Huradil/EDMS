from django.urls import path

from .views import MainView

app_name = "core"
urlpatterns = [
    path('', MainView.as_view(), name='home'),
]
