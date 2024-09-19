from http import HTTPStatus
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from user.auth_email import EmailAuthBackend

User = get_user_model()


class RegisterUserViewTestCase(TestCase):

    def setUp(self):
        self.url_view = reverse('signup')
        self.user_data = {
            'username': 'newuser',
            'password1': 'password_123!',
            'password2': 'password_123!',
            'email': 'newuser@example.com'
        }

    def test_success_get_http_method(self):
        response = self.client.get(self.url_view)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'auth/register.html')

    @patch('thisapp.utils.get_user_invitations')
    def test_success_post_http_method(self, mock_get_user_invitations):
        mock_get_user_invitations.return_value = []
        response = self.client.post(self.url_view, self.user_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('profile'))
        self.assertTrue(User.objects.filter(username=self.user_data['username'], group__name='normal').exists())

    def test_post_http_method_with_field_error(self):
        self.user_data['password2'] = 'differentpassword'
        response = self.client.post(self.url_view, self.user_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'auth/register.html')
        self.assertContains(response, "The two password fields didn’t match")
        self.assertFalse(User.objects.filter(username=self.user_data['username']).exists())


class LoginUserViewTestCase(TestCase):
    fixtures = ['data.json']

    def setUp(self):
        self.username = 'TestUser1'
        self.password = '321qwe,./'
        self.client = Client()
        self.url_view = reverse('login')

    def test_success_get_http_method(self):
        response = self.client.get(self.url_view)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'auth/login.html')

    @patch('thisapp.utils.get_user_invitations')
    def test_success_post_http_method(self, mock_get_user_invitations):
        mock_get_user_invitations.return_value = []
        response = self.client.post(self.url_view, {'username': self.username, 'password': self.password})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('profile'))

    def test_post_http_method_with_field_error(self):
        response = self.client.post(
            self.url_view,
            {'username': 'non_existent_user', 'password': self.password}
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'auth/login.html')
        self.assertContains(response, 'Please enter a correct username or email and password')


class EmailAuthBackendTestCase(TestCase):
    fixtures = ['data.json']

    def setUp(self):
        self.backend = EmailAuthBackend()
        self.username = 'TestUser1'
        self.password = '321qwe,./'
        self.email = 'testuser1@mail.com'

    def test_authenticate_success(self):
        user = self.backend.authenticate(request=None, username=self.email, password=self.password)
        self.assertIsNotNone(user)
        self.user = User.objects.get(username=self.username)
        self.assertEqual(user, self.user)

    def test_authenticate_invalid_email(self):
        user = self.backend.authenticate(request=None, username='wrong@example.com', password=self.password)
        self.assertIsNone(user)


class CustomPasswordChangeViewTestCase(TestCase):
    fixtures = ['data.json']

    def setUp(self):
        self.username = 'TestUser1'
        self.password = '321qwe,./'
        self.client = Client()
        self.client.login(username=self.username, password=self.password)
        self.url_view = reverse('password_change')

    def test_success_get_http_method(self):
        response = self.client.get(self.url_view)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'user/password_change.html')

    def test_success_post_http_method(self):
        new_password = 'newpassword123'
        response = self.client.post(
            self.url_view,
            {
                'old_password': self.password,
                'new_password1': new_password,
                'new_password2': new_password
            }
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('password_change_done'))
        user = User.objects.get(username=self.username)
        self.assertEqual(user.check_password(new_password), True)

    def test_post_http_method_with_field_error(self):
        response = self.client.post(
            self.url_view,
            {
                'old_password': self.password,
                'new_password1': 'newpassword123',
                'new_password2': 'differentpassword'
            }
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'user/password_change.html')
        self.assertContains(response, "The two password fields didn’t match")
