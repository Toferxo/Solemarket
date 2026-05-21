from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Listing, ListingImage, SellerProfile, Review
from .forms import ListingForm, ListingImageFormSet, RegisterForm, ReviewForm


def index(request):
    listings = Listing.objects.filter(activa=True, vendida=False).select_related('vendedor')
    marca = request.GET.get('marca', '')
    condicion = request.GET.get('condicion', '')
    q = request.GET.get('q', '')
    orden = request.GET.get('orden', '-creado')

    if marca:
        listings = listings.filter(marca=marca)
    if condicion:
        listings = listings.filter(condicion=condicion)
    if q:
        listings = listings.filter(
            Q(nombre__icontains=q) | Q(marca__icontains=q) | Q(vendedor__username__icontains=q)
        )
    if orden in ['precio', '-precio', '-creado']:
        listings = listings.order_by(orden)

    marcas = Listing.MARCA_CHOICES
    total = Listing.objects.filter(activa=True, vendida=False).count()

    return render(request, 'listings/index.html', {
        'listings': listings,
        'marcas': marcas,
        'total': total,
        'filtros': {'marca': marca, 'condicion': condicion, 'q': q, 'orden': orden},
    })


def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk, activa=True)
    otras = Listing.objects.filter(
        vendedor=listing.vendedor, activa=True, vendida=False
    ).exclude(pk=pk)[:4]

    profile, _ = SellerProfile.objects.get_or_create(user=listing.vendedor)
    review_form = ReviewForm()

    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            r = review_form.save(commit=False)
            r.vendedor = profile
            r.autor = request.user
            r.listing = listing
            r.save()
            messages.success(request, '¡Reseña publicada!')
            return redirect('listing_detail', pk=pk)

    return render(request, 'listings/detail.html', {
        'listing': listing,
        'otras': otras,
        'profile': profile,
        'review_form': review_form,
    })


@login_required
def listing_create(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.vendedor = request.user
            listing.save()

            imagenes = request.FILES.getlist('imagenes')
            for i, img in enumerate(imagenes[:4]):
                ListingImage.objects.create(listing=listing, imagen=img, orden=i)

            messages.success(request, '¡Par publicado exitosamente!')
            return redirect('listing_detail', pk=listing.pk)
    else:
        form = ListingForm()

    return render(request, 'listings/create.html', {'form': form})


@login_required
def listing_edit(request, pk):
    listing = get_object_or_404(Listing, pk=pk, vendedor=request.user)
    if request.method == 'POST':
        form = ListingForm(request.POST, instance=listing)
        if form.is_valid():
            form.save()
            imagenes = request.FILES.getlist('imagenes')
            for i, img in enumerate(imagenes[:4]):
                ListingImage.objects.create(listing=listing, imagen=img, orden=i)
            messages.success(request, 'Publicación actualizada.')
            return redirect('listing_detail', pk=listing.pk)
    else:
        form = ListingForm(instance=listing)
    return render(request, 'listings/create.html', {'form': form, 'editing': True, 'listing': listing})


@login_required
@require_POST
def listing_delete(request, pk):
    listing = get_object_or_404(Listing, pk=pk, vendedor=request.user)
    listing.activa = False
    listing.save()
    messages.success(request, 'Publicación eliminada.')
    return redirect('mis_publicaciones')


@login_required
def mis_publicaciones(request):
    listings = Listing.objects.filter(vendedor=request.user).order_by('-creado')
    return render(request, 'listings/mis_publicaciones.html', {'listings': listings})


def seller_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile, _ = SellerProfile.objects.get_or_create(user=user)
    listings = Listing.objects.filter(vendedor=user, activa=True, vendida=False)
    reviews = profile.reviews.select_related('autor', 'listing').all()
    dist = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r in reviews:
        dist[r.estrellas] = dist.get(r.estrellas, 0) + 1
    total_rev = sum(dist.values())

    return render(request, 'listings/seller_profile.html', {
        'profile_user': user,
        'profile': profile,
        'listings': listings,
        'reviews': reviews,
        'dist': dist,
        'total_rev': total_rev,
    })


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            SellerProfile.objects.create(
                user=user,
                ciudad=form.cleaned_data.get('ciudad', 'Santiago'),
                contacto=form.cleaned_data.get('contacto', ''),
            )
            login(request, user)
            messages.success(request, f'¡Bienvenido a SoleMarket, {user.username}!')
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'listings/register.html', {'form': form})


@login_required
def toggle_favorito(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    favs = request.session.get('favoritos', [])
    if pk in favs:
        favs.remove(pk)
        en_favs = False
    else:
        favs.append(pk)
        en_favs = True
    request.session['favoritos'] = favs
    return JsonResponse({'en_favoritos': en_favs, 'total': len(favs)})


def favoritos(request):
    pks = request.session.get('favoritos', [])
    listings = Listing.objects.filter(pk__in=pks, activa=True)
    return render(request, 'listings/favoritos.html', {'listings': listings})
