from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('publicar/', views.listing_create, name='listing_create'),
    path('par/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('par/<int:pk>/editar/', views.listing_edit, name='listing_edit'),
    path('par/<int:pk>/eliminar/', views.listing_delete, name='listing_delete'),
    path('par/<int:pk>/favorito/', views.toggle_favorito, name='toggle_favorito'),
    path('mis-publicaciones/', views.mis_publicaciones, name='mis_publicaciones'),
    path('favoritos/', views.favoritos, name='favoritos'),
    path('vendedor/<str:username>/', views.seller_profile, name='seller_profile'),
    path('registro/', views.register, name='register'),
]
