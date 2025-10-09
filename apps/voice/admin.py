# agentapp/admin.py
from django.contrib import admin
from .models import Agent

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "enabled", "updated_at")
    search_fields = ("name", "owner__username", "owner__email")
    list_filter = ("enabled",)
