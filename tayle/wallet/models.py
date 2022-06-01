from django.db import models
from django.contrib.auth import get_user_model

from .validators import validate_positive_score

User = get_user_model()


class Wallet(models.Model):
    balance = models.FloatField(default=0.0,
                                verbose_name='Баланс',
                                validators=[validate_positive_score])
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='wallets')
    name = models.CharField(max_length=256,
                            verbose_name='Наименование кошелька')

    class Meta:
        db_table = 'wallet'

    def __str__(self):
        return self.name


class Transfer(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='transfers')
    src_wallet = models.ManyToManyField(Wallet,
                                        verbose_name='Мои счета',
                                        related_name='src_transfers',
                                        )
    dst_wallet = models.ForeignKey(Wallet,
                                   on_delete=models.SET_NULL,
                                   verbose_name='Счет получателя',
                                   related_name='dst_transfers',
                                   null=True)
    created_at = models.DateTimeField(auto_now=True)
    score = models.FloatField(validators=[validate_positive_score],
                              verbose_name='Сумма перевода')

    class Meta:
        db_table = 'transfer'
        ordering = ['-created_at']


