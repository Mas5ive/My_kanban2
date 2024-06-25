from collections import defaultdict
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from thisapp.forms import CreateBoardForm
from thisapp.models import Membership

from .forms import LoginUserForm, RegisterUserForm


@login_required
def profile_view(request):
    form_data = request.session.pop('form_data', None)
    form_errors = request.session.pop('form_errors', None)

    if form_data:
        form = CreateBoardForm(form_data)
        form.errors.update(form_errors)
    else:
        form = CreateBoardForm()

    user_boards = Membership.objects.filter(user=request.user)

    boards = defaultdict(list)
    for user in user_boards:
        if user.is_owner:
            boards['owner boards'].append(user.board)
        else:
            boards['invitation boards'].append(user.board)

    context = {
        'form': form,
        'owner_boards': boards['owner boards'],
        'invitation_boards': boards['invitation boards']
    }
    return render(request, 'user/profile.html', context=context)


class RegisterUserView(CreateView):
    form_class = RegisterUserForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = authenticate(
            username=form.cleaned_data.get('username'),
            password=form.cleaned_data.get('password1')
        )
        login(self.request, user)
        return response


class LoginUserView(LoginView):
    form_class = LoginUserForm
    template_name = 'auth/login.html'
