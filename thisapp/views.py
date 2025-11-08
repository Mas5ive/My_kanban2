import mimetypes

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import BadRequest, PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from my_kanban2.http_handlers import (custom_require_http_methods,
                                      payload_too_large_view)

from . import invitations as invs
from . import utils
from .forms import CardForm, CommentForm, CreateBoardForm
from .models import Board, Card, Comment, Membership


@custom_require_http_methods(['GET'])
def index_view(request):
    return render(request, 'index.html')


@login_required
@custom_require_http_methods(['GET'])
def profile_view(request):
    context = {
        'form': CreateBoardForm(),
        'invitations': invs.get_user_invitations(request.user.username),
    }
    return render(request, 'profile.html', context=context)


@login_required
@custom_require_http_methods(['GET'])
def board_view(request, board_id):
    board = get_object_or_404(
        Board.objects.prefetch_related('membership_set__user', 'cards'),
        id=board_id,
    )

    user = request.user
    user_with_board = Membership.objects.filter(user=user, board=board).first()

    if not user_with_board:
        raise PermissionDenied

    grouped_cards = utils.get_card_groups(board)

    context = {
        'board': board,
        'user_is_owner': user_with_board.is_owner,
        'backlog_cards': grouped_cards.get(Card.Status.BACKLOG, []),
        'in_progress_cards': grouped_cards.get(Card.Status.IN_PROGRESS, []),
        'done_cards': grouped_cards.get(Card.Status.DONE, []),
    }
    return render(request, 'board.html', context=context)


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
        if 'file' in form.errors and any('size' in error for error in form.errors['file']):
            return payload_too_large_view(request)

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
