from django.contrib import admin
from .models import Listing, ListingImage, SellerProfile, Review


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'marca', 'vendedor', 'precio', 'condicion', 'activa', 'vendida', 'creado']
    list_filter = ['marca', 'condicion', 'activa', 'vendida']
    search_fields = ['nombre', 'vendedor__username']
    inlines = [ListingImageInline]


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'ciudad', 'verificado', 'creado']
    list_filter = ['verificado']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['autor', 'vendedor', 'estrellas', 'creado']
    list_filter = ['estrellas']
