from functools import wraps
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .forms import CardForm, CommentForm, CreateBoardForm
from .models import Board, Card, Invitation, Membership

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

    def test_success_get_http_method(self):
        response = self.client.get(self.url_view)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertIsInstance(response.context['form'], CreateBoardForm)
        self.assertEqual(response.context['owner_boards'], [Board.objects.get(title='Wow project')])
        self.assertEqual(response.context['invitation_boards'], [Board.objects.get(title='Boring project')])

        self.user = User.objects.get(username=self.username)
        user_invitation = Invitation.objects.filter(user_recipient=self.user).select_related('board', 'user_sender')
        self.assertQuerySetEqual(response.context['invitations'], user_invitation)


