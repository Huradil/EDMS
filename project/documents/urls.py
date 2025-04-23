from django.urls import path

from .views import DocumentCreateView

app_name = "documents"
urlpatterns = [
    path('document_create/', DocumentCreateView.as_view(), name='document_create'),

]
