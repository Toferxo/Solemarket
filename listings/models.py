from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    ciudad = models.CharField(max_length=100, default='Santiago')
    contacto = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    verificado = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)

    @property
    def rating_promedio(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return round(sum(r.estrellas for r in reviews) / len(reviews), 1)

    @property
    def total_ventas(self):
        return self.user.listings.filter(vendida=True).count()

    def __str__(self):
        return f'Perfil de {self.user.username}'


class Listing(models.Model):
    CONDICION_CHOICES = [
        ('new', 'Nueva'),
        ('used', 'Usada'),
        ('rare', 'Edición limitada'),
    ]
    DESPACHO_CHOICES = [
        ('yes', 'Todo Chile'),
        ('local', 'Solo presencial'),
        ('both', 'Envío y presencial'),
    ]
    MARCA_CHOICES = [
        ('Nike', 'Nike'), ('Adidas', 'Adidas'), ('Jordan', 'Jordan'),
        ('New Balance', 'New Balance'), ('Puma', 'Puma'), ('Vans', 'Vans'),
        ('Converse', 'Converse'), ('Asics', 'Asics'), ('Reebok', 'Reebok'),
        ('Otra', 'Otra'),
    ]

    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    marca = models.CharField(max_length=50, choices=MARCA_CHOICES)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    talla = models.CharField(max_length=10)
    precio = models.PositiveIntegerField()
    condicion = models.CharField(max_length=10, choices=CONDICION_CHOICES, default='used')
    despacho = models.CharField(max_length=10, choices=DESPACHO_CHOICES, default='yes')
    ciudad = models.CharField(max_length=100, default='Santiago')
    activa = models.BooleanField(default=True)
    vendida = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado']

    def get_absolute_url(self):
        return reverse('listing_detail', args=[self.pk])

    def precio_fmt(self):
        return f'${self.precio:,}'.replace(',', '.')

    def __str__(self):
        return f'{self.marca} {self.nombre} - {self.vendedor.username}'


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    imagen = models.ImageField(upload_to='listings/%Y/%m/')
    orden = models.PositiveSmallIntegerField(default=0)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['orden', 'creado']

    def __str__(self):
        return f'Imagen #{self.orden} de {self.listing}'


class Review(models.Model):
    vendedor = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='reviews')
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_escritas')
    listing = models.ForeignKey(Listing, on_delete=models.SET_NULL, null=True, blank=True)
    estrellas = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comentario = models.TextField()
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado']
        unique_together = ['vendedor', 'autor', 'listing']

    def __str__(self):
        return f'{self.estrellas}★ de {self.autor.username} a {self.vendedor.user.username}'
