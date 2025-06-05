import requests
from django.utils.text import slugify
from accounts.models import UserProfile

# 그룹원들을 GitHub 저장소에 collaborator로 초대하는 함수
def invite_collaborators_to_repo(group_name, owner_user, member_users):
    from accounts.models import UserProfile
    import requests
    from django.utils.text import slugify

    try:
        owner_profile = owner_user.userprofile
        access_token = owner_profile.github_token
        github_owner = owner_profile.github_username
    except UserProfile.DoesNotExist:
        return False

    repo_name = f'docverse-{slugify(group_name)}'
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github+json'
    }

    success, failed = [], []

    for member in member_users:
        try:
            member_username = member.userprofile.github_username
        except UserProfile.DoesNotExist:
            failed.append(member.username)
            continue

        url = f'https://api.github.com/repos/{github_owner}/{repo_name}/collaborators/{member_username}'
        payload = {
            "permission": "push"
        }

        res = requests.put(url, headers=headers, json=payload)
        if res.status_code in [201, 204]:  # 성공 (204는 이미 있음)
            success.append(member_username)
        else:
            failed.append(member_username)

    return {'invited': success, 'failed': failed}
