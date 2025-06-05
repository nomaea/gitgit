import requests

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
