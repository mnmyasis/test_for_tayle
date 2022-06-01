from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import DetailView

from .forms import TransferForm
from .models import Transfer

COUNT_TRANSFER = 10


def index(request):
    return render(request, 'wallet/index.html', {})


@login_required
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


@login_required
def transfer_list(request):
    search = {}
    if request.GET.get('dst_wallet'):
        search['dst_wallet__name__icontains'] = request.GET.get('dst_wallet')
    if request.GET.get('src_wallet'):
        search['src_wallet'] = request.GET.get('src_wallet')
    if request.GET.get('score'):
        search['score'] = float(request.GET.get('score'))
    if request.GET.get('created_at'):
        search['created_at'] = request.GET.get('created_at')

    if search:
        transfers = request.user.transfers.filter(**search)
    else:
        transfers = request.user.transfers.all()
    paginator = Paginator(transfers, COUNT_TRANSFER)
    num_page = request.GET.get('page')
    page_obj = paginator.get_page(num_page)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'wallet/transfer_list.html', context)


class TransferDetailView(DetailView):
    model = Transfer
    template_name = 'wallet/transfer_detail.html'
