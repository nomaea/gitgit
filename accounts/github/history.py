import requests
from django.utils.text import slugify
from accounts.models import UserProfile

# ✅ 커밋 히스토리 조회 함수
def get_commit_history(group_name, user, branch_name='main', file_path=None):
    try:
        profile = user.userprofile
        access_token = profile.github_token
        github_username = profile.github_username
    except UserProfile.DoesNotExist:
        return {'status': 'error', 'message': 'GitHub 인증 정보 없음'}

    repo_name = f'docverse-{slugify(group_name)}'
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github+json'
    }

    url = f'https://api.github.com/repos/{github_username}/{repo_name}/commits'
    params = {'sha': branch_name}
    if file_path:
        params['path'] = file_path

    res = requests.get(url, headers=headers, params=params)

    if res.status_code != 200:
        return {'status': 'error', 'message': res.json()}

    # 필요한 정보만 추려서 반환
    commits = [{
        'sha': c['sha'],
        'message': c['commit']['message'],
        'author': c['commit']['author']['name'],
        'date': c['commit']['author']['date']
    } for c in res.json()]

    return {'status': 'success', 'commits': commits}
