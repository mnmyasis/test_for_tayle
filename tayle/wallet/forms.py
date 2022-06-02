from typing import List

from django import forms

from .models import Transfer, User, Wallet


class TransferForm(forms.ModelForm):

    def __init__(self, *args, user: User, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['src_wallet'].queryset = (
            self.fields['src_wallet'].queryset.filter(user=user))
        self.fields['dst_wallet'].queryset = (
            self.fields['dst_wallet'].queryset.exclude(user=user))

    class Meta:
        model = Transfer
        fields = (
            'src_wallet',
            'dst_wallet',
            'score'
        )
        widgets = {
            'src_wallet': forms.CheckboxSelectMultiple,
        }

    def debiting_money(self) -> List[Wallet]:
        wallets = self.cleaned_data.get('src_wallet')
        score = self.cleaned_data['score']
        wallet_count = wallets.count()
        for wallet in wallets:
            wallet.balance = wallet.balance - score / wallet_count
        return wallets

    def clean_score(self) -> float:
        if not self.cleaned_data.get('src_wallet'):
            return self.cleaned_data['score']
        wallets = self.debiting_money()
        for wallet in wallets:
            if wallet.balance < 0:
                raise forms.ValidationError(
                    (f'На кошельке {wallet.name} недостаточно средств для '
                     f'списания'),
                    params={'wallet': wallet.name}
                )
        return self.cleaned_data['score']

    def save(self, commit=True):
        obj = super().save(commit)
        self.cleaned_data['dst_wallet'].balance = (
                self.cleaned_data['dst_wallet'].balance +
                self.cleaned_data['score'])
        self.cleaned_data['dst_wallet'].save()
        for wallet in self.cleaned_data['src_wallet']:
            wallet.save()
        return obj

