from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from social_django.models import UserSocialAuth
from .models import UserProfile


def github_login_view(request):
    return render(request, 'accounts/github_login.html')

@login_required
def github_success(request):
    github_login = request.user.social_auth.get(provider='github')
    access_token = github_login.extra_data['access_token']
    username = github_login.extra_data['login']

    # UserProfile에 저장
    profile = request.user.userprofile
    profile.github_token = access_token
    profile.github_username = username
    profile.save()
    
    return redirect('upload_and_list')