from django.contrib import admin

from .models import Branch

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'address',)
    search_fields = ('name', 'address',)
    list_filter = ('is_active',)
    list_per_page = 20

