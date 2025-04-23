from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at',)
    list_filter = ('created_by',)
    search_fields = ('name', 'created_by__username')
    list_per_page = 20
