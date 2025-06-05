#기능 요약: 특정 파일을 base64 인코딩하여 GitHub 저장소의 브랜치에 업로드(commit)

import base64
import requests
from django.utils.text import slugify
from accounts.models import UserProfile

# ✅ GitHub 저장소의 브랜치에 파일을 커밋하고 푸시하는 함수
def commit_file_to_branch(group_name, user, file_path, file_content, commit_message, branch_name='main'):
    try:
        profile = user.userprofile
        access_token = profile.github_token
        github_username = profile.github_username
    except UserProfile.DoesNotExist:
        return {'status': 'error', 'message': 'User not connected to GitHub'}

    repo_name = f'docverse-{slugify(group_name)}'
    api_url = f'https://api.github.com/repos/{github_username}/{repo_name}/contents/{file_path}'

    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github+json'
    }

    # 1. 기존 파일의 SHA 확인 (있으면 업데이트, 없으면 새로 커밋)
    sha = None
    sha_check = requests.get(f"{api_url}?ref={branch_name}", headers=headers)
    if sha_check.status_code == 200:
        sha = sha_check.json().get('sha')

    # 2. 커밋 요청
    encoded_content = base64.b64encode(file_content.encode()).decode()

    payload = {
        'message': commit_message,
        'content': encoded_content,
        'branch': branch_name
    }
    if sha:
        payload['sha'] = sha

    res = requests.put(api_url, headers=headers, json=payload)

    if res.status_code in [201, 200]:
        return {'status': 'success', 'commit': res.json()}
    else:
        return {'status': 'error', 'message': res.json()}
