from collections import defaultdict
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseNotFound, HttpResponseRedirect)
from django.shortcuts import (get_list_or_404, get_object_or_404, redirect,
                              render)
from django.urls import reverse

from user.models import CustomUser

from .forms import CardForm, CreateBoardForm
from .models import Board, Card, Invitation, Membership


def index_view(request):
    return render(request, 'index.html')


@login_required
def profile_view(request):
    form_data = request.session.pop('form_data', None)
    form_errors = request.session.pop('form_errors', None)

    if form_data:
        form = CreateBoardForm(form_data)
        form.errors.update(form_errors)
    else:
        form = CreateBoardForm()

    user_boards = Membership.objects.filter(user=request.user).select_related('board')

    boards = defaultdict(list)
    for user in user_boards:
        if user.is_owner:
            boards['owner boards'].append(user.board)
        else:
            boards['invitation boards'].append(user.board)

    invitations = Invitation.objects.filter(user_recipient=request.user).select_related('board', 'user_sender')

    context = {
        'form': form,
        'owner_boards': boards['owner boards'],
        'invitation_boards': boards['invitation boards'],
        'invitations': invitations,
    }
    return render(request, 'profile.html', context=context)


@login_required
def handle_board_view(request, board_id):
    board = get_object_or_404(
        Board.objects.prefetch_related('membership_set__user', 'cards'),
        id=board_id,
    )

    user_with_board = Membership.objects.filter(user=request.user, board=board).first()

    if not user_with_board:
        return HttpResponseForbidden()

    if request.method == 'POST':
        if not user_with_board.is_owner:
            return HttpResponseForbidden()
        else:
            board.delete()
            return redirect('profile')

    grouped_cards = defaultdict(list)
    for card in board.cards.all():
        grouped_cards[card.status].append(card)

    context = {
        'board': board,
        'user_is_owner': user_with_board.is_owner,
        'backlog_cards': grouped_cards.get(Card.Status.BACKLOG, []),
        'in_progress_cards': grouped_cards.get(Card.Status.IN_PROGRESS, []),
        'done_cards': grouped_cards.get(Card.Status.DONE, []),
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


def handle_messages_and_redirect(view_func):
    @wraps(view_func)
    def _wrapped_view(request, board_id, *args, **kwargs):
        response = view_func(request, board_id, *args, **kwargs)
        if isinstance(response, tuple) and len(response) == 2:
            message, message_type = response
            if message_type == 'success':
                messages.success(request, message)
            elif message_type == 'error':
                messages.error(request, message)
            return redirect('board', board_id=board_id)
        return response
    return _wrapped_view


@login_required
@handle_messages_and_redirect
def сreate_invitation_view(request, board_id):
    if request.method == 'POST':
        membership = get_list_or_404(Membership, board=board_id)
        sender = request.user

        if not any(m.is_owner and m.user == sender for m in membership):
            return HttpResponseForbidden()

        recipient_username = request.POST.get('recipient', '')
        recipient = CustomUser.objects.filter(username=recipient_username).first()

        if not recipient:
            return "The user doesn't exist", 'error'

        if any(m.user == recipient for m in membership):
            return "The user is already a member of the board", 'error'

        try:
            Invitation.objects.create(
                user_recipient=recipient,
                board_id=board_id,
                user_sender=sender
            )
        except IntegrityError:
            return 'The user has already received an invitation', 'error'

        return 'The invitation has been sent!', 'success'
    else:
        return HttpResponseNotFound()


@login_required
def delete_member_view(request, board_id):
    if request.method == 'POST':
        membership = get_list_or_404(Membership, board=board_id)

        if not any(m.is_owner for m in membership if m.user == request.user):
            return HttpResponseForbidden()

        member = CustomUser.objects.filter(username=request.POST.get('member', '')).first()

        if not member or all(m.user != member for m in membership if not m.is_owner):
            return HttpResponse('The request contains incorrect data', status=400)

        Membership.objects.filter(
            user=member,
            board_id=board_id
        ).delete()

        return redirect('board', board_id=board_id)
    else:
        return HttpResponseNotFound()


@login_required
def pick_invitation_view(request, board_id):
    if request.method == 'POST':
        recipient = request.user
        invitation = Invitation.objects.filter(board_id=board_id, user_recipient=recipient).first()

        if not invitation:
            return HttpResponse('The request contains incorrect data', status=400)

        operation = request.POST['operation']
        if operation == 'accept':
            with transaction.atomic():
                invitation.delete()
                Membership.objects.create(
                    user=recipient,
                    board_id=board_id
                )
        elif operation == 'reject':
            invitation.delete()
        else:
            return HttpResponse('The request contains incorrect data', status=400)

        return redirect('profile')
    else:
        return HttpResponseNotFound()


@login_required
def create_card_view(request, board_id):
    membership = get_object_or_404(Membership, board=board_id, user=request.user)

    if not membership.is_owner:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.board_id = board_id
            card.save()
            return redirect('board', board_id=board_id)
        else:
            status = 400
    else:
        form = CardForm()
        status = 200

    context = {
        'board_id': board_id,
        'form': form,
    }
    return render(request, 'card/create.html', context=context, status=status)


def move_card(card: Card, operation: str):
    match card.status, operation:
        case Card.Status.BACKLOG, 'MOVE_RIGHT':
            card.status = Card.Status.IN_PROGRESS
        case Card.Status.IN_PROGRESS, 'MOVE_LEFT':
            card.status = Card.Status.BACKLOG
        case Card.Status.IN_PROGRESS, 'MOVE_RIGHT':
            card.status = Card.Status.DONE
        case Card.Status.DONE, 'MOVE_LEFT':
            card.status = Card.Status.IN_PROGRESS
        case _:
            return False
    card.save()
    return True


def edit_card(request, card: Card):
    form = CardForm(request.POST)

    if form.is_valid():
        changed_card = form.save(commit=False)
        card.title = changed_card.title
        card.content = changed_card.content
        card.save()
        messages.success(request, 'Saved')
        status = 200
    else:
        errors_str = '\n'.join([f"{field}: {error}"
                                for field, error_list in form.errors.items() for error in error_list])
        messages.error(request, errors_str)
        status = 400

    context = {
        'card': card,
        'form': form
    }
    return context, status


def handle_post_request_card(request, card: Card, board_id: int, user_with_board: Membership):
    operation = request.POST.get('operation', '')

    if operation == 'DELETE':
        if not user_with_board.is_owner:
            return HttpResponseForbidden()

        card.delete()
        return redirect('board', board_id=board_id)

    elif operation == 'EDIT':
        if not user_with_board.is_owner:
            return HttpResponseForbidden()

        context, status = edit_card(request, card)
        context['board_id'] = board_id
        context['user_with_board'] = user_with_board
        return render(request, 'card/view.html', context=context, status=status)

    elif 'MOVE' in operation:
        result = move_card(card, operation)
        if result:
            return redirect('board', board_id=board_id)

    return HttpResponse('The request contains incorrect data', status=400)


@login_required
def handle_card_view(request, board_id, card_id):
    card = get_object_or_404(Card, id=card_id)
    user_with_board = Membership.objects.filter(board_id=board_id, user=request.user).first()

    if not user_with_board:
        return HttpResponseForbidden()

    if request.method == 'POST':
        return handle_post_request_card(request, card, board_id, user_with_board)

    form = CardForm(instance=card)
    context = {
        'board_id': board_id,
        'user_with_board': user_with_board,
        'card': card,
        'form': form
    }
    return render(request, 'card/view.html', context=context)
