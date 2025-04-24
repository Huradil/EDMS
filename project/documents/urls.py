from django.urls import path

from .views import DocumentCreateView, DocumentDetailView, DocumentSignView

app_name = "documents"
urlpatterns = [
    path('document_create/', DocumentCreateView.as_view(), name='document_create'),
    path('document_detail/<int:pk>/', DocumentDetailView.as_view(), name='document_detail'),
    path('document_sign/<int:pk>/', DocumentSignView.as_view(), name='document_sign'),

]
