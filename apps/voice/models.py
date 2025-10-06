from django.db import models

class Agent(models.Model):
    name = models.CharField(max_length=100)
    welcome_message = models.TextField(blank=True, default="")
    agent_prompt = models.TextField(help_text="System/instructions for the agent")
    business_details = models.JSONField(default=dict, blank=True)
    voice = models.CharField(max_length=50, default="alloy")
    language = models.CharField(max_length=10, default="bn")
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
