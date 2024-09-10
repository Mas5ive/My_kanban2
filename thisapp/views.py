import mimetypes
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import BadRequest, PermissionDenied
from django.db import transaction
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import (get_list_or_404, get_object_or_404, redirect,
                              render)
from django.urls import reverse

from thisapp.http_handlers import custom_require_http_methods
from user.models import CustomUser

from . import utils
from .forms import CardForm, CommentForm, CreateBoardForm
from .models import Board, Card, Comment, Membership


@custom_require_http_methods(['GET'])
def index_view(request):
    return render(request, 'index.html')


@login_required
@custom_require_http_methods(['GET'])
def profile_view(request):
    user_boards = Membership.objects.filter(user=request.user).select_related('board')

    boards = defaultdict(list)
    for user in user_boards:
        if user.is_owner:
            boards['owner boards'].append(user.board)
        else:
            boards['invitation boards'].append(user.board)

    context = {
        'form': CreateBoardForm(),
        'owner_boards': boards['owner boards'],
        'invitation_boards': boards['invitation boards'],
        'invitations': utils.get_user_invitations(request.user.username),
    }
    return render(request, 'profile.html', context=context)


@login_required
@custom_require_http_methods(['GET', 'POST'])
def handle_board_view(request, board_id):
    board = get_object_or_404(
        Board.objects.prefetch_related('membership_set__user', 'cards'),
        id=board_id,
    )

    user = request.user
    user_with_board = Membership.objects.filter(user=user, board=board).first()

    if not user_with_board:
        raise PermissionDenied

    if request.method == 'POST':
        if not user_with_board.is_owner:
            raise PermissionDenied
        else:
            board.delete()
            utils.delete_board_invitations(board_id)
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
@custom_require_http_methods(['POST'])
def create_board_view(request):
    form = CreateBoardForm(request.POST)

    if not form.is_valid():
        for field, list_error in form.errors.items():
            for error in list_error:
                messages.error(request, field + ': ' + error)
        raise BadRequest

    with transaction.atomic():
        board = form.save()
        Membership.objects.create(
            user=request.user,
            board=board,
            is_owner=True
        )
    return HttpResponseRedirect(reverse('profile'), status=303)


@login_required
@custom_require_http_methods(['POST'])
def сreate_invitation_view(request, board_id):
    membership = get_list_or_404(Membership, board=board_id)
    sender = request.user

    if not any(m.is_owner and m.user == sender for m in membership):
        raise PermissionDenied

    recipient_name = request.POST.get('recipient', '')
    recipient = CustomUser.objects.filter(username=recipient_name).first()

    if not recipient:
        messages.error(request, f'User "{recipient_name}" does not exist')
        raise BadRequest

    if any(m.user == recipient for m in membership):
        messages.error(request, f'User "{recipient_name}" is already a member of the board')
        raise BadRequest

    if utils.get_invitation(board_id, recipient_name):
        messages.error(request, f'User "{recipient_name}" has already received an invitation')
        raise BadRequest

    utils.create_invitation(board_id, sender.username, recipient_name)
    messages.success(request, 'The invitation has been sent!')

    response = redirect('board', board_id=board_id)
    response.status_code = 303
    return response


@login_required
@custom_require_http_methods(['POST'])
def delete_member_view(request, board_id):
    membership = get_list_or_404(Membership, board=board_id)

    if not any(m.is_owner for m in membership if m.user == request.user):
        raise PermissionDenied

    member_name = request.POST.get('member', '')
    member = CustomUser.objects.filter(username=member_name).first()

    if not member or all(m.user != member for m in membership if not m.is_owner):
        messages.error(request, f'The use of the user "{member_name}" in the request is incorrect')
        raise BadRequest

    Membership.objects.filter(
        user=member,
        board_id=board_id
    ).delete()

    response = redirect('board', board_id=board_id)
    response.status_code = 303
    return response


@login_required
@custom_require_http_methods(['POST'])
def pick_invitation_view(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    user = CustomUser.objects.get(username=request.user)

    if not utils.get_invitation(board.id, user.username):
        messages.error(request, f'The user {user.username} does not have an invitation to the board')
        raise BadRequest

    operation = request.POST.get('operation', '')

    if operation == 'accept':
        Membership.objects.create(
            user=user,
            board_id=board_id
        )
    elif operation == 'reject':
        pass
    else:
        messages.error(request, f'The “{operation}” operation is incorrect in this request')
        raise BadRequest

    utils.delete_invitation(board_id, user.username)

    response = redirect('profile')
    response.status_code = 303
    return response


@login_required
@custom_require_http_methods(['GET', 'POST'])
def create_card_view(request, board_id):
    board = get_object_or_404(Board, id=board_id)

    if not Membership.objects.filter(board=board, user=request.user, is_owner=True).exists():
        raise PermissionDenied

    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.board_id = board_id
            card.save()
            response = redirect('board', board_id=board_id)
            response.status_code = 303
            return response
        else:
            for field, list_error in form.errors.items():
                for error in list_error:
                    messages.error(request, field + ': ' + error)
            raise BadRequest

    context = {
        'board_id': board_id,
        'form': CardForm(),
    }
    return render(request, 'card/create.html', context=context)


def handle_post_request_card(request, card: Card, board: Board, user_with_board: Membership):
    operation = request.POST.get('operation', '')
    errors = {}

    if operation == 'DELETE':
        if not user_with_board.is_owner:
            raise PermissionDenied
        result = utils.delete_card(card)

    elif operation == 'EDIT':
        if not user_with_board.is_owner:
            raise PermissionDenied
        card_form = CardForm(request.POST)
        result, errors = utils.edit_card(card_form, card)

    elif 'MOVE' in operation:
        result = utils.move_card(card, operation)

    else:
        result = False

    if not result:
        if errors:
            for field, list_error in errors.items():
                for error in list_error:
                    messages.error(request, field + ': ' + error)
        else:
            messages.error(request, f'The “{operation}” operation is incorrect in this request')
        raise BadRequest

    response = redirect('board', board_id=board.id)
    response.status_code = 303
    return response


@login_required
@custom_require_http_methods(['GET', 'POST'])
def handle_card_view(request, board_id, card_id):
    board = get_object_or_404(Board, id=board_id)
    card = get_object_or_404(Card.objects.prefetch_related('comments__author'), id=card_id, board=board)
    user_with_board = Membership.objects.filter(board_id=board_id, user=request.user).select_related('user').first()

    if not user_with_board:
        raise PermissionDenied

    if request.method == 'POST':
        return handle_post_request_card(request, card, board, user_with_board)

    comment_form = CommentForm()

    context = {
        'board': board,
        'user_with_board': user_with_board,
        'card': card,
        'comment_form': comment_form,
    }

    if user_with_board.is_owner:
        context['card_form'] = CardForm(instance=card)

    return render(request, 'card/view.html', context=context)


@login_required
@custom_require_http_methods(['POST'])
def create_comment_view(request, board_id, card_id):
    board = get_object_or_404(Board, id=board_id)

    if not Membership.objects.filter(user=request.user, board_id=board_id).exists():
        raise PermissionDenied

    card = get_object_or_404(Card, id=card_id, board=board)
    form = CommentForm(request.POST, request.FILES)

    if not form.is_valid():
        for field, list_error in form.errors.items():
            for error in list_error:
                messages.error(request, field + ': ' + error)
            raise BadRequest

    comment = form.save(commit=False)
    comment.card_id = card.id
    comment.author = request.user
    comment.save()
    return redirect('card', board_id=board_id, card_id=card_id)


@login_required
@custom_require_http_methods(['GET'])
def get_file_from_comment(request, board_id, card_id, comment_id):
    board = get_object_or_404(Board, id=board_id)

    if not Membership.objects.filter(user=request.user, board_id=board_id).exists():
        raise PermissionDenied

    card = get_object_or_404(Card, id=card_id, board=board)
    comment = get_object_or_404(Comment, id=comment_id, card=card)

    file_name = comment.get_filename()
    if not file_name:
        raise Http404

    mime_type, _ = mimetypes.guess_type(file_name)
    if mime_type is None:
        mime_type = 'application/octet-stream'

    with open(comment.file.path, 'rb') as file:
        response = HttpResponse(file.read(), content_type=mime_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


@login_required
@custom_require_http_methods(['POST'])
def delete_comment_view(request, board_id, card_id, comment_id):
    board = get_object_or_404(Board, id=board_id)
    card = get_object_or_404(Card, id=card_id, board=board)
    comment = get_object_or_404(Comment, id=comment_id, card=card)

    if comment.author != request.user:
        raise PermissionDenied

    operation = request.POST.get('operation', '')
    if operation != 'DELETE':
        messages.error(request, f'The “{operation}” operation is incorrect in this request')
        raise BadRequest

    comment.delete()
    return redirect('card', board_id=board_id, card_id=card_id)
