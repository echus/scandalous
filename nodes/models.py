__author__ = 'Anmol'

from django.db import models


class Node(models.Model):
    node = models.IntegerField(default=0, primary_key=True)
    device = models.CharField(max_length=30)

    # This specifies to display the "device" in the online admin application
    def __str__(self):
        return self.device

    class Meta:
        ordering = ('node',)


class Channel(models.Model):
    node = models.ForeignKey(Node)
    channel = models.IntegerField(default=0)
    value = models.CharField(max_length=50)
    direction_choices = (
        ('in', 'in'),
        ('out', 'out'),
    )
    direction = models.CharField(max_length=3, choices=direction_choices, default='out')

    # This specifies to display the "device" in the online admin application
    def __str__(self):
        return self.value

    class Meta:
        ordering = ('channel',)