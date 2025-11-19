import mimetypes

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render

from my_kanban2.http_handlers import custom_require_http_methods

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
@custom_require_http_methods(['GET'])
def create_card_view(request, board_id):
    board = get_object_or_404(Board, id=board_id)

    if not Membership.objects.filter(board=board, user=request.user, is_owner=True).exists():
        raise PermissionDenied

    context = {
        'board_id': board_id,
        'form': CardForm(),
    }
    return render(request, 'card/create.html', context=context)


@login_required
@custom_require_http_methods(['GET'])
def card_view(request, board_id, card_id):
    board = get_object_or_404(Board, id=board_id)
    card = get_object_or_404(Card, id=card_id, board=board)
    user_with_board = Membership.objects.filter(board_id=board_id, user=request.user).select_related('user').first()

    if not user_with_board:
        raise PermissionDenied

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
@custom_require_http_methods(['GET'])
def get_file_from_comment(request, board_id, card_id, comment_id):
    card = get_object_or_404(Card, id=card_id, board_id=board_id)
    comment = get_object_or_404(Comment, id=comment_id, card=card)

    if not Membership.objects.filter(user=request.user, board_id=board_id).exists():
        raise PermissionDenied

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
