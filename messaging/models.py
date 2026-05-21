from django.db import models
from django.contrib.auth.models import User
from listings.models import Listing


class Conversation(models.Model):
    comprador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversaciones_comprador')
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversaciones_vendedor')
    listing = models.ForeignKey(Listing, on_delete=models.SET_NULL, null=True, related_name='conversaciones')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-actualizado']
        unique_together = ['comprador', 'vendedor', 'listing']

    def otro_usuario(self, user):
        return self.vendedor if user == self.comprador else self.comprador

    def mensajes_no_leidos(self, user):
        return self.mensajes.filter(leido=False).exclude(autor=user).count()

    def __str__(self):
        return f'{self.comprador.username} → {self.vendedor.username} | {self.listing}'


class Message(models.Model):
    conversacion = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='mensajes')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    leido = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['creado']

    def __str__(self):
        return f'{self.autor.username}: {self.contenido[:50]}'
