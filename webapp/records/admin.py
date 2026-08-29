from django.contrib import admin
from .models import DataEntry

@admin.register(DataEntry)
class DataEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "value", "created_at")
    list_filter = ("category",)
    search_fields = ("title", "description", "notes")
