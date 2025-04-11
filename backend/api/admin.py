from django.contrib import admin
from .models import OzonApiKey , Product

@admin.register(OzonApiKey)
class OzonApiKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'client_id', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'client_id')

admin.site.register(Product)