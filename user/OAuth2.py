from uuid import uuid4

from django.contrib.auth.models import Group
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from social_core.utils import module_member, slugify
from social_django.models import UserSocialAuth

USER_FIELDS = ["username"]


def logout_then_OAuth2(request, provider):
    login_url = reverse_lazy('social:begin', args=[provider])
    return LogoutView.as_view(next_page=login_url)(request)


def social_user(backend, uid, *args, **kwargs):
    OAuth2_user = UserSocialAuth.objects.filter(provider=backend.name, uid=uid).first()

    if OAuth2_user:
        return {'user': OAuth2_user.user}

    return {
        'is_new': True,
        'user': None
    }


def get_username(strategy, details, backend, user=None, *args, **kwargs):
    if "username" not in backend.setting("USER_FIELDS", USER_FIELDS):
        return
    storage = strategy.storage

    if not user:
        email_as_username = strategy.setting("USERNAME_IS_FULL_EMAIL", False)
        uuid_length = strategy.setting("UUID_LENGTH", 4)
        max_length = storage.user.username_max_length()
        do_slugify = strategy.setting("SLUGIFY_USERNAMES", False)
        do_clean = strategy.setting("CLEAN_USERNAMES", True)

        def identity_func(val):
            return val

        if do_clean:
            override_clean = strategy.setting("CLEAN_USERNAME_FUNCTION")
            if override_clean:
                clean_func = module_member(override_clean)
            else:
                clean_func = storage.user.clean_username
        else:
            clean_func = identity_func

        if do_slugify:
            override_slug = strategy.setting("SLUGIFY_FUNCTION")
            slug_func = module_member(override_slug) if override_slug else slugify
        else:
            slug_func = identity_func

        if email_as_username and details.get("email"):
            username = details["email"]
        elif details.get("username"):
            username = details["username"]
        else:
            username = uuid4().hex

        short_username = (
            username[: max_length - uuid_length - 1] if max_length is not None else username
        )
        final_username = slug_func(clean_func(username[:max_length]))

        while not final_username or storage.user.user_exists(username=final_username):
            username = short_username + '_' + uuid4().hex[:uuid_length]
            final_username = slug_func(clean_func(username[:max_length]))

    else:
        final_username = storage.user.get_username(user)
    return {"username": final_username}


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {"is_new": False}

    fields = {
        name: kwargs.get(name, details.get(name))
        for name in backend.setting("USER_FIELDS", USER_FIELDS)
    }
    if not fields:
        return

    fields['group'] = Group.objects.get(name='OAuth2')
    return {"is_new": True, "user": strategy.create_user(**fields)}
