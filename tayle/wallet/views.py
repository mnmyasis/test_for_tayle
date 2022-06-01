from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import TransferForm


def index(request):
    return render(request, 'wallet/index.html', {})


def transfer(request):
    form = TransferForm(request.POST or None,
                        user=request.user)
    if form.is_valid():
        transfer_obj = form.save(commit=False)
        transfer_obj.user = request.user
        transfer_obj.save()
        form.save_m2m()
        return redirect(reverse('wallet:index'))
    context = {
        'form': form
    }
    return render(request, 'wallet/transfer.html', context)
