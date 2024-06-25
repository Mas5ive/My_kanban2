from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CreateBoardForm
from .models import Board, Membership


def index_view(request):
    return render(request, 'index.html')


@login_required
def handle_board_view(request, board_id):
    board = get_object_or_404(Board, id=board_id)

    try:
        membership = Membership.objects.select_related('board').get(user=request.user, board=board)
    except Membership.DoesNotExist:
        return HttpResponseForbidden()

    if request.method == 'POST':
        if not membership.is_owner:
            return HttpResponseForbidden()
        else:
            board.delete()
            return redirect('profile')

    context = {
        'board': board,
        'is_owner': membership.is_owner
    }
    return render(request, 'board.html', context=context)


@login_required
def create_board_view(request):
    if request.method == 'POST':
        form = CreateBoardForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                board = form.save()
                Membership.objects.create(
                    user=request.user,
                    board=board,
                    is_owner=True
                )
            return redirect('profile')
        else:
            request.session['form_data'] = request.POST
            request.session['form_errors'] = form.errors
            return HttpResponseRedirect(reverse('profile'), status=303)
    else:
        return HttpResponseNotFound()
