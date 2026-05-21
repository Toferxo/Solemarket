from django.contrib import admin
from .models import Conversation, Message

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['comprador', 'vendedor', 'listing', 'creado']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['autor', 'conversacion', 'leido', 'creado']
    list_filter = ['leido']
