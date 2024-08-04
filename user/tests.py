from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

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

    def test_success_post_http_method(self):
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


