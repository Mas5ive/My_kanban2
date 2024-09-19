from functools import wraps
from http import HTTPStatus
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .forms import CardForm, CommentForm, CreateBoardForm
from .models import Board, Card, Membership

User = get_user_model()


def parametrize(arg_names, arg_values):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args):
            func(self, *args)
        wrapper._parametrized = (arg_names, arg_values)
        return wrapper
    return decorator


class ParametrizedTestCaseMeta(type):
    """
    Creates tested methods based on a parametrized method of the Testcase class. They have an index at the end,
      so you can easily track down errors.
    In general, this metaclass makes the testing process more reliable, clear and compact.
    """

    def __new__(cls, name, bases, attrs):
        new_attrs = {}
        for attr_name, attr_value in attrs.items():
            if hasattr(attr_value, '_parametrized'):
                arg_names, arg_values = attr_value._parametrized
                for index, values in enumerate(arg_values, 1):
                    test_method_name = f'{attr_name}_{index}'
                    new_attrs[test_method_name] = cls.create_test_method(attr_value, values)
            else:
                new_attrs[attr_name] = attr_value
        return super().__new__(cls, name, bases, new_attrs)

    @staticmethod
    def create_test_method(func, values):
        @wraps(func)
        def test_method(self):
            return func(self, *values)
        return test_method


class ProfileViewTestCase(TestCase, metaclass=ParametrizedTestCaseMeta):
    fixtures = ['data.json']

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

    @patch('thisapp.utils.get_user_invitations')
    def test_success_get_http_method(self, mock_get_user_invitations):
        mock_get_user_invitations.return_value = []
        response = self.client.get(self.url_view)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertIsInstance(response.context['form'], CreateBoardForm)
        self.assertEqual(response.context['owner_boards'], [Board.objects.get(title='Wow project')])
        self.assertEqual(response.context['invitation_boards'], [Board.objects.get(title='Boring project')])
        self.assertEqual(response.context['invitations'], [])


class CreateCardViewTestCase(TestCase, metaclass=ParametrizedTestCaseMeta):
    fixtures = ['data.json']

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
    fixtures = ['data.json']

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
