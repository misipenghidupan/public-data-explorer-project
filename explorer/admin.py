from django.contrib import admin
from .models import SavedQuery

@admin.register(SavedQuery)
class SavedQueryAdmin(admin.ModelAdmin):
    """
    Admin configuration for the SavedQuery model.
    The list_display field is corrected to use 'title' instead of 'name'.
    """
    list_display = ('title', 'created_at')
    search_fields = ('title', 'query')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
