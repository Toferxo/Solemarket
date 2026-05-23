from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Conversation, Message
from listings.models import Listing
import json


@login_required
def inbox(request):
    conversaciones = Conversation.objects.filter(
        Q(comprador=request.user) | Q(vendedor=request.user)
    ).select_related('comprador', 'vendedor', 'listing').prefetch_related('mensajes')

    conv_activa = None
    conv_id = request.GET.get('conv')
    if conv_id:
        conv_activa = get_object_or_404(Conversation, pk=conv_id)
        if request.user not in [conv_activa.comprador, conv_activa.vendedor]:
            return redirect('inbox')
        conv_activa.mensajes.filter(leido=False).exclude(autor=request.user).update(leido=True)

    # Preparar datos para el template (Django no permite llamar métodos con args en templates)
    convs_data = []
    total_no_leidos = 0
    for conv in conversaciones:
        otro = conv.vendedor if request.user == conv.comprador else conv.comprador
        no_leidos = conv.mensajes.filter(leido=False).exclude(autor=request.user).count()
        total_no_leidos += no_leidos
        convs_data.append({
            'conv': conv,
            'otro': otro,
            'no_leidos': no_leidos,
            'ultimo': conv.mensajes.last(),
        })

    otro_activo = None
    if conv_activa:
        otro_activo = conv_activa.vendedor if request.user == conv_activa.comprador else conv_activa.comprador

    return render(request, 'messaging/inbox.html', {
        'convs_data': convs_data,
        'conv_activa': conv_activa,
        'otro_activo': otro_activo,
        'total_no_leidos': total_no_leidos,
    })


@login_required
def start_conversation(request, listing_pk):
    listing = get_object_or_404(Listing, pk=listing_pk, activa=True)
    if listing.vendedor == request.user:
        return redirect('listing_detail', pk=listing_pk)

    conv, created = Conversation.objects.get_or_create(
        comprador=request.user,
        vendedor=listing.vendedor,
        listing=listing,
    )
    if created:
        Message.objects.create(
            conversacion=conv,
            autor=request.user,
            contenido=f'Hola! Me interesa tu par: {listing.marca} {listing.nombre} a ${listing.precio:,}. ¿Sigue disponible?'.replace(',', '.'),
        )
    return redirect(f'/mensajes/?conv={conv.pk}')


@login_required
@require_POST
def send_message(request, conv_pk):
    conv = get_object_or_404(Conversation, pk=conv_pk)
    if request.user not in [conv.comprador, conv.vendedor]:
        return JsonResponse({'error': 'No autorizado'}, status=403)

    data = json.loads(request.body)
    contenido = data.get('contenido', '').strip()
    if not contenido:
        return JsonResponse({'error': 'Mensaje vacío'}, status=400)

    msg = Message.objects.create(
        conversacion=conv,
        autor=request.user,
        contenido=contenido,
    )
    conv.save()

    return JsonResponse({
        'id': msg.pk,
        'contenido': msg.contenido,
        'autor': msg.autor.username,
        'es_mio': True,
        'creado': msg.creado.strftime('%H:%M'),
    })


@login_required
def poll_messages(request, conv_pk):
    conv = get_object_or_404(Conversation, pk=conv_pk)
    if request.user not in [conv.comprador, conv.vendedor]:
        return JsonResponse({'error': 'No autorizado'}, status=403)

    desde = request.GET.get('desde')
    msgs = conv.mensajes.all()
    if desde:
        msgs = msgs.filter(pk__gt=int(desde))

    msgs.filter(leido=False).exclude(autor=request.user).update(leido=True)

    return JsonResponse({
        'mensajes': [
            {
                'id': m.pk,
                'contenido': m.contenido,
                'autor': m.autor.username,
                'es_mio': m.autor == request.user,
                'creado': m.creado.strftime('%H:%M'),
            }
            for m in msgs
        ]
    })
