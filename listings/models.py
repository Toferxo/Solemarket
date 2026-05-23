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

    # Categorías principales
    CATEGORIA_CHOICES = [
        ('zapatillas', 'Zapatillas'),
        ('streetwear', 'Streetwear'),
        ('accesorios', 'Accesorios Sneaker'),
        ('coleccion', 'Colección'),
    ]

    # Subcategorías por categoría
    SUBCATEGORIA_CHOICES = [
        # Zapatillas
        ('running', 'Running'),
        ('basketball', 'Basketball'),
        ('lifestyle', 'Lifestyle'),
        ('skate', 'Skate'),
        ('training', 'Training / Gym'),
        ('boots', 'Boots'),
        # Streetwear
        ('polera', 'Polera / T-Shirt'),
        ('hoodie', 'Hoodie / Poleron'),
        ('pants', 'Pants / Joggers'),
        ('chaqueta', 'Chaqueta / Jacket'),
        ('gorro', 'Gorro / Cap'),
        ('calcetines', 'Calcetines'),
        # Accesorios sneaker
        ('cordones', 'Cordones / Laces'),
        ('cleaning', 'Cleaning Kit'),
        ('insoles', 'Plantillas / Insoles'),
        ('shields', 'Crease Protectors / Shields'),
        ('cajas', 'Cajas / Display'),
        ('bolso', 'Bolso / Cartera'),
        ('lentes', 'Lentes'),
        # Colección
        ('figura', 'Figura / Funko'),
        ('poster', 'Poster / Art Print'),
        ('libro', 'Libro / Revista'),
        ('otro_col', 'Otro coleccionable'),
    ]

    CONDICION_CHOICES = [
        ('ds', 'DS — Deadstock (sin usar, caja original)'),
        ('vnds', 'VNDS — Very Near Deadstock (1-2 usos)'),
        ('used', 'Used — Usada (buen estado)'),
        ('beater', 'Beater — Muy usada'),
    ]

    DESPACHO_CHOICES = [
        ('yes', 'Todo Chile'),
        ('local', 'Solo presencial'),
        ('both', 'Envío y presencial'),
    ]

    MARCA_CHOICES = [
        # Zapatillas
        ('Nike', 'Nike'), ('Jordan', 'Jordan'), ('Adidas', 'Adidas'),
        ('New Balance', 'New Balance'), ('Asics', 'Asics'), ('Puma', 'Puma'),
        ('Vans', 'Vans'), ('Converse', 'Converse'), ('Reebok', 'Reebok'),
        ('Saucony', 'Saucony'), ('On Running', 'On Running'), ('Salehe', 'Salehe'),
        ('Yeezy', 'Yeezy'), ('Off-White', 'Off-White'), ('Travis Scott', 'Travis Scott'),
        # Streetwear
        ('Supreme', 'Supreme'), ('Palace', 'Palace'), ('Stüssy', 'Stüssy'),
        ('BAPE', 'BAPE'), ('Carhartt', 'Carhartt WIP'), ('Dickies', 'Dickies'),
        ('Anti Social', 'Anti Social Social Club'), ('Kith', 'Kith'),
        # Accesorios
        ('Crep Protect', 'Crep Protect'), ('Jason Markk', 'Jason Markk'),
        ('Reshoevn8r', 'Reshoevn8r'), ('Huf', 'HUF'), ('Stance', 'Stance'),
        ('Otra', 'Otra'),
    ]

    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='zapatillas')
    subcategoria = models.CharField(max_length=20, choices=SUBCATEGORIA_CHOICES, default='lifestyle', blank=True)
    marca = models.CharField(max_length=50, choices=MARCA_CHOICES)
    nombre = models.CharField(max_length=200)
    colorway = models.CharField(max_length=100, blank=True, help_text='ej: Black/White, Bred, University Blue')
    descripcion = models.TextField(blank=True)
    talla = models.CharField(max_length=10, blank=True)
    precio = models.PositiveIntegerField()
    precio_original = models.PositiveIntegerField(null=True, blank=True, help_text='Precio de retail original')
    condicion = models.CharField(max_length=10, choices=CONDICION_CHOICES, default='used')
    caja_original = models.BooleanField(default=False)
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

    def precio_original_fmt(self):
        if self.precio_original:
            return f'${self.precio_original:,}'.replace(',', '.')
        return None

    def descuento_pct(self):
        if self.precio_original and self.precio_original > 0:
            return round((1 - self.precio / self.precio_original) * 100)
        return None

    def condicion_badge(self):
        badges = {
            'ds': ('DS', 'badge-ds'),
            'vnds': ('VNDS', 'badge-vnds'),
            'used': ('USED', 'badge-used'),
            'beater': ('BEATER', 'badge-beater'),
        }
        return badges.get(self.condicion, ('', ''))

    def es_zapatilla(self):
        return self.categoria == 'zapatillas'

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
