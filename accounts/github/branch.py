import requests, json
from accounts.models import UserProfile
from django.utils.text import slugify

# ✅ GitHub 저장소에 새 브랜치를 생성하는 함수
def create_github_branch(access_token, github_username, repo_name, new_branch_name):
    base_branch = 'main'
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github+json'
    }

    # base 브랜치 SHA 가져오기
    sha_resp = requests.get(
        f'https://api.github.com/repos/{github_username}/{repo_name}/git/refs/heads/{base_branch}',
        headers=headers
    )
    if sha_resp.status_code != 200:
        return False

    base_sha = sha_resp.json()['object']['sha']

    # 브랜치 생성 요청
    payload = {
        "ref": f"refs/heads/{new_branch_name}",
        "sha": base_sha
    }

    create_resp = requests.post(
        f'https://api.github.com/repos/{github_username}/{repo_name}/git/refs',
        headers=headers,
        json=payload
    )
    return create_resp.status_code == 201

# ✅ 브랜치 목록 가져오기
def list_github_branches(group_name, user):
    try:
        profile = user.userprofile
        token = profile.github_token
        username = profile.github_username
    except UserProfile.DoesNotExist:
        return []

    repo = f'docverse-{slugify(group_name)}'
    url = f'https://api.github.com/repos/{username}/{repo}/branches'

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github+json'
    }

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return []

    return [b['name'] for b in res.json()]

# ✅ 특정 브랜치의 루트 파일 목록 가져오기
def list_files_in_branch(group_name, user, branch_name='main'):
    try:
        profile = user.userprofile
        token = profile.github_token
        username = profile.github_username
    except UserProfile.DoesNotExist:
        return []

    repo = f'docverse-{slugify(group_name)}'
    url = f'https://api.github.com/repos/{username}/{repo}/contents/?ref={branch_name}'

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github+json'
    }

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return []

    return [{'name': f['name'], 'type': f['type'], 'path': f['path']} for f in res.json()]