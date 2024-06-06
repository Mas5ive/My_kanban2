from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend


class EmailAuthBackend(BaseBackend):
    def authenticate(self, request, password=None, **kwargs):
        user_model = get_user_model()
        email = kwargs.get(user_model.USERNAME_FIELD)

        try:
            user = user_model.objects.get(email=email)
        except user_model.DoesNotExist:
            return

        if user.check_password(password):
            return user

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return
        return user
