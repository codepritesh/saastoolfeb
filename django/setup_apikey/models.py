from __future__ import unicode_literals

from django_better_admin_arrayfield.models.fields import ArrayField
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings

def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]


class APIKEY(models.Model):
    EX_ID_ENUM = [
        ('BIN', 'Binance'),
        ('BIM', 'Binance Margin'),
        ('BIF', 'Binance Future'),
        ('HIT', 'Hitbtc'),
        ('KRA', 'Kraken'),
        ('DAX', 'Indodax'),
        ('HUO', 'Huobi'),
        ('KEX', 'Okex3'),
        ('KUC', 'Kucoin'),
        ('MOX', 'Moonix'),
    ]
    STAUS = [
        ('AVAILABLE', 'Available'),
        ('ON_RUNNING', 'On Running'),
    ]
    name = models.CharField(max_length=100, db_index=True, unique=True)
    own_name = models.ForeignKey(User, blank=True, null=True,  on_delete=models.SET(get_sentinel_user))
    ex_id = models.CharField(choices=EX_ID_ENUM, default='BIN', max_length=3)
    api_keys = models.TextField()
    secret_keys = models.TextField()
    passphrase = models.TextField(blank=True)
    exclude_pnl = models.BooleanField(default=False)
    # add filed for monitor admin
    added_by = models.CharField(max_length=100, blank=True, default=18)
    tags = ArrayField(models.CharField(max_length=200), blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']