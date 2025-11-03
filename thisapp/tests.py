from http import HTTPStatus
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from my_kanban2.utils import ParametrizedTestCaseMeta, parametrize

from .forms import CardForm, CommentForm, CreateBoardForm
from .models import Card, Membership

User = get_user_model()


class ProfileViewTestCase(TestCase, metaclass=ParametrizedTestCaseMeta):
    fixtures = ['demo/demo-data.json']

    def setUp(self):
        self.username = 'TestUser1'
        self.password = '321qwe,./'
        self.client = Client()
        self.client.login(username=self.username, password=self.password)
        self.url_view = reverse('profile')

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url_view)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url_view}")

    @parametrize('method_name', [['put'], ['post'], ['head'], ['patch'], ['delete']])
    def test_mot_allowed_http_methods(self, method_name):
        method = getattr(self.client, method_name)
        response = method(self.url_view)
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    @patch('thisapp.invitations.get_user_invitations')
    def test_success_get_http_method(self, mock_get_user_invitations):
        mock_get_user_invitations.return_value = []
        response = self.client.get(self.url_view)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertIsInstance(response.context['form'], CreateBoardForm)
        self.assertEqual(response.context['invitations'], [])


class BoardViewTestCase(TestCase, metaclass=ParametrizedTestCaseMeta):
    fixtures = ['demo/demo-data.json']

    def setUp(self):
        self.username = 'TestUser1'
        self.password = '321qwe,./'
        self.client = Client()
        self.client.login(username=self.username, password=self.password)
        self.url_view = 'board'
        self.owner_board_id = 1
        self.member_board_id = 2
        self.no_access_board_id = 3
        self.not_exists_board_id = 100

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(reverse(self.url_view, args=[self.owner_board_id]))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse(self.url_view, args=[self.owner_board_id])}")

    @parametrize('method_name', [['put'], ['post'], ['head'], ['patch'], ['delete']])
    def test_mot_allowed_http_methods(self, method_name: str):
        method = getattr(self.client, method_name)
        response = method(reverse(self.url_view, args=[self.owner_board_id]))
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_success_get_http_method(self):
        response = self.client.get(reverse(self.url_view, args=[self.owner_board_id]))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'board.html')
        self.assertEqual(response.context['board'].id, self.owner_board_id)
        self.assertTrue(response.context['user_is_owner'])
        self.assertFalse(response.context['board'].membership_set.filter(
            user=self.client.session['_auth_user_id'],
            is_owner=False).exists()
        )

    def test_success_get_http_method_for_member(self):
        response = self.client.get(reverse(self.url_view, args=[self.member_board_id]))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'board.html')
        self.assertEqual(response.context['board'].id, self.member_board_id)
        self.assertFalse(response.context['user_is_owner'])
        self.assertTrue(response.context['board'].membership_set.filter(
            user=self.client.session['_auth_user_id'],
            is_owner=False).exists()
        )

    @parametrize(
        ('board_id', 'expected_status_code'),
        [
            (3, HTTPStatus.FORBIDDEN),  # no access board_id
            (100, HTTPStatus.NOT_FOUND),  # not exists board_id
        ]
    )
    def test_invalid_get_http_method(self, board_id, expected_status_code):
        response = self.client.get(reverse(self.url_view, args=[board_id]))
        self.assertEqual(response.status_code, expected_status_code)


class CreateCardViewTestCase(TestCase, metaclass=ParametrizedTestCaseMeta):
    fixtures = ['demo/demo-data.json']

    def setUp(self):
        self.username = 'TestUser1'
        self.password = '321qwe,./'
        self.client = Client()
        self.client.login(username=self.username, password=self.password)
        self.title_view = 'card_create'
        self.owner_board_id = 1

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(reverse(self.title_view, args=[self.owner_board_id]))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next=" +
            f"{reverse(self.title_view, args=[self.owner_board_id])}"
        )

    @parametrize('method_name', [['put'], ['head'], ['patch'], ['delete']])
    def test_mot_allowed_http_methods(self, method_name: str):
        method = getattr(self.client, method_name)
        response = method(reverse(self.title_view, args=[self.owner_board_id]))
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_success_get_http_method(self):
        response = self.client.get(reverse(self.title_view, args=[self.owner_board_id]))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIsInstance(response.context['form'], CardForm)
        self.assertTemplateUsed(response, 'card/create.html')

    @parametrize(
        ('board_id', 'expected_status_code'),
        [
            (3, HTTPStatus.FORBIDDEN),  # no access board_id
            (100, HTTPStatus.NOT_FOUND),  # not exists board_id
        ]
    )
    def test_invalid_get_http_method(self, board_id, expected_status_code):
        response = self.client.get(reverse(self.title_view, args=[board_id]))
        self.assertEqual(response.status_code, expected_status_code)

    @parametrize(
        ('data', 'is_number_of_cards_changed', 'expected_status_code'),
        [
            ({}, True, HTTPStatus.BAD_REQUEST),
            ({'title': 'New card', 'contant': 'Some content'}, False, HTTPStatus.SEE_OTHER),
        ]
    )
    def test_post_http_method(self, data, is_number_of_cards_changed, expected_status_code):
        count_cards_before_request = Card.objects.filter(board_id=self.owner_board_id).count()
        response = self.client.post(reverse(self.title_view, args=[self.owner_board_id]), data)
        self.assertEqual(response.status_code, expected_status_code)
        count_cards_after_request = Card.objects.filter(board_id=self.owner_board_id).count()
        self.assertEqual(count_cards_before_request == count_cards_after_request, is_number_of_cards_changed)


class HandleCardViewTestCase(TestCase, metaclass=ParametrizedTestCaseMeta):
    fixtures = ['demo/demo-data.json']

    OWNER_BOARD_ID = 1
    OWNER_BOARD_BACKLOG_CARD_ID = 2
    OWNER_BOARD_IN_PROGRESS_CARD_ID = 1
    OWNER_BOARD_DONE_CARD_ID = 5

    MEMBER_BOARD_ID = 2
    MEMBER_BOARD_CARD_ID = 3

    NO_ACCESS_BOARD_ID = 3
    NO_ACCESS_CARD_ID = 4
    NOT_EXISTS_BOARD_ID = 100
    INCOHERENT_CARD_ID = 100

    def setUp(self):
        self.username = 'TestUser1'
        self.password = '321qwe,./'
        self.client = Client()
        self.client.login(username=self.username, password=self.password)
        self.title_view = 'card'

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(reverse(
            self.title_view,
            args=[self.OWNER_BOARD_ID, self.OWNER_BOARD_IN_PROGRESS_CARD_ID])
        )
        self.assertRedirects(
            response,
            f"{reverse('login')}?next=" +
            f"{reverse(self.title_view, args=[self.OWNER_BOARD_ID, self.OWNER_BOARD_IN_PROGRESS_CARD_ID])}"
        )

    @parametrize('method_name', [['put'], ['head'], ['patch'], ['delete']])
    def test_mot_allowed_http_methods(self, method_name: str):
        method = getattr(self.client, method_name)
        response = method(reverse(self.title_view, args=[self.OWNER_BOARD_ID,  self.OWNER_BOARD_IN_PROGRESS_CARD_ID]))
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_success_get_http_method(self):
        response = self.client.get(reverse(
            self.title_view,
            args=[self.OWNER_BOARD_ID, self.OWNER_BOARD_IN_PROGRESS_CARD_ID])
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'card/view.html')
        self.assertEqual(response.context['board'].id, self.OWNER_BOARD_ID)
        self.assertEqual(response.context['card'].id, self.OWNER_BOARD_IN_PROGRESS_CARD_ID)
        self.assertIsInstance(response.context['card_form'], CardForm)
        self.assertEqual(response.context['card_form'].instance.id, self.OWNER_BOARD_IN_PROGRESS_CARD_ID)
        self.assertIsInstance(response.context['comment_form'], CommentForm)

        self.user = User.objects.get(username=self.username)
        user_with_board = Membership.objects.filter(
            board_id=self.OWNER_BOARD_ID,
            user=self.user
        ).select_related('user').first()
        self.assertEqual(response.context['user_with_board'], user_with_board)

    @parametrize(
        ('board_id', 'card_id', 'expected_status_code'),
        [
            (OWNER_BOARD_ID, INCOHERENT_CARD_ID, HTTPStatus.NOT_FOUND),
            (NO_ACCESS_BOARD_ID, NO_ACCESS_CARD_ID, HTTPStatus.FORBIDDEN),
            (NOT_EXISTS_BOARD_ID, OWNER_BOARD_IN_PROGRESS_CARD_ID, HTTPStatus.NOT_FOUND),
        ]
    )
    def test_invalid_get_http_method(self, board_id, card_id, expected_status_code):
        response = self.client.get(reverse(self.title_view, args=[board_id, card_id]))
        self.assertEqual(response.status_code, expected_status_code)

    def test_card_form_unavailable_for_member(self):
        response = self.client.get(reverse(self.title_view, args=[self.MEMBER_BOARD_ID, self.MEMBER_BOARD_CARD_ID]))
        self.assertNotIn('card_form', response.context)

    @parametrize(
        ('board_id', 'card_id', 'expected_status_code'),
        [
            (MEMBER_BOARD_ID, MEMBER_BOARD_CARD_ID, HTTPStatus.FORBIDDEN),
            (OWNER_BOARD_ID, OWNER_BOARD_IN_PROGRESS_CARD_ID, HTTPStatus.SEE_OTHER),
        ]
    )
    def test_delete_post_http_method(self, board_id, card_id, expected_status_code):
        response = self.client.post(
            reverse(self.title_view, args=[board_id, card_id]),
            {'operation': 'DELETE'},
        )
        self.assertEqual(response.status_code, expected_status_code)

    @parametrize(
        ('board_id', 'card_id', 'expected_status_code'),
        [
            (MEMBER_BOARD_ID, MEMBER_BOARD_CARD_ID, HTTPStatus.FORBIDDEN),
            (OWNER_BOARD_ID, OWNER_BOARD_IN_PROGRESS_CARD_ID, HTTPStatus.SEE_OTHER),
        ]
    )
    def test_edit_post_http_method(self, board_id, card_id, expected_status_code):
        response = self.client.post(
            reverse(self.title_view, args=[board_id, card_id]),
            {
                'operation': 'EDIT',
                'title': 'tttle',
                'content': 'content'
            },
        )
        self.assertEqual(response.status_code, expected_status_code)

    @parametrize(
        ('board_id', 'card_id', 'operation', 'expected_status_code'),
        [
            (OWNER_BOARD_ID, OWNER_BOARD_DONE_CARD_ID, 'MOVE_RIGHT', HTTPStatus.BAD_REQUEST),
            (OWNER_BOARD_ID, OWNER_BOARD_BACKLOG_CARD_ID, 'MOVE_LEFT', HTTPStatus.BAD_REQUEST),
            (OWNER_BOARD_ID, OWNER_BOARD_IN_PROGRESS_CARD_ID, 'MOVE_LEFT', HTTPStatus.SEE_OTHER),
            (OWNER_BOARD_ID, OWNER_BOARD_IN_PROGRESS_CARD_ID, 'MOVE_RIGHT', HTTPStatus.SEE_OTHER),
        ]
    )
    def test_move_post_http_method(self, board_id, card_id, operation, expected_status_code):
        response = self.client.post(
            reverse(self.title_view, args=[board_id, card_id]),
            {'operation': operation}
        )
        self.assertEqual(response.status_code, expected_status_code)

    def test_invalid_operation_post_http_method(self):
        response = self.client.post(
            reverse(self.title_view, args=[self.OWNER_BOARD_ID, self.OWNER_BOARD_IN_PROGRESS_CARD_ID]),
            {'operation': 'REMOVE'}
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
