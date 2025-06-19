import base64
import requests
from django.utils.text import slugify
from accounts.models import UserProfile

def rollback_file_to_commit(group_name, user, file_path, target_sha, branch_name='main'):
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

    # 1. 커밋에서 blob URL 조회
    commit_url = f'https://api.github.com/repos/{github_username}/{repo_name}/commits/{target_sha}'
    commit_res = requests.get(commit_url, headers=headers)
    if commit_res.status_code != 200:
        return {'status': 'error', 'message': '커밋 조회 실패'}

    files = commit_res.json().get('files', [])
    target_file = next((f for f in files if f['filename'] == file_path), None)
    if not target_file:
        return {'status': 'error', 'message': '커밋에 해당 파일 없음'}

    # 2. 해당 파일 내용 가져오기
    blob_url = target_file['raw_url']
    blob_content = requests.get(blob_url).text

    # 3. 현재 파일 SHA 가져오기 (있으면 덮어쓰기용)
    sha_check = requests.get(
        f'https://api.github.com/repos/{github_username}/{repo_name}/contents/{file_path}?ref={branch_name}',
        headers=headers
    )
    sha = sha_check.json().get('sha') if sha_check.status_code == 200 else None

    # 4. 커밋
    encoded_content = base64.b64encode(blob_content.encode()).decode()
    payload = {
        'message': f'{file_path} reverted to {target_sha[:7]}',
        'content': encoded_content,
        'branch': branch_name
    }
    if sha:
        payload['sha'] = sha

    res = requests.put(
        f'https://api.github.com/repos/{github_username}/{repo_name}/contents/{file_path}',
        headers=headers,
        json=payload
    )

    if res.status_code in [200, 201]:
        return {'status': 'success', 'message': f'{file_path} 되돌리기 완료'}
    else:
        return {'status': 'error', 'message': res.json()}
