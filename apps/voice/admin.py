from django.contrib import admin
from .models import Agent

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled', 'updated_at')
    search_fields = ('name',)
    list_filter = ('enabled',)
