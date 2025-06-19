import requests
from django.utils.text import slugify
from accounts.models import UserProfile

# ✅ 그룹 이름과 사용자 정보를 받아 GitHub 저장소를 자동 생성하는 함수
def create_github_repo_for_group(group_name, user):
    try:
        profile = user.userprofile
        access_token = profile.github_token
        github_username = profile.github_username
    except UserProfile.DoesNotExist:
        return False  # GitHub 연동이 안 된 사용자일 경우

    # 저장소 이름은 'docverse-그룹이름' 형식 (slug 형태)
    repo_name = f'docverse-{slugify(group_name)}'
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github+json'
    }
    payload = {
        'name': repo_name,
        'private': True,
        'description': f'Docverse Group Repository for {group_name}',
        'auto_init': True
    }

    # GitHub 저장소 생성 요청
    res = requests.post(
        'https://api.github.com/user/repos',
        headers=headers,
        json=payload
    )

    # 성공 시 True 반환, 실패 시 False
    return res.status_code == 201