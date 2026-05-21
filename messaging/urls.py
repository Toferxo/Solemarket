from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('iniciar/<int:listing_pk>/', views.start_conversation, name='start_conversation'),
    path('enviar/<int:conv_pk>/', views.send_message, name='send_message'),
    path('poll/<int:conv_pk>/', views.poll_messages, name='poll_messages'),
]
