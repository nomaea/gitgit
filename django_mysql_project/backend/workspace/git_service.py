import os
import subprocess
from django.utils.timezone import now
from django.conf import settings
from .models import UploadedFile, GitVersion, GitActionLog

REPO_ROOT = settings.BASE_DIR

# 최근 커밋 해시를 반환
def get_latest_commit_hash():
    result = subprocess.run(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE, cwd=REPO_ROOT)
    return result.stdout.decode().strip()

# Git 연동 파일 업로드 또는 덮어쓰기 처리
# - 기존 파일이 있으면 덮어쓰기, 없으면 새로 생성
# - Git add, commit, push 수행
# - GitVersion, GitActionLog에 기록
def git_upload(f, filepath, filename, commit_msg, username):
    existing = UploadedFile.objects.filter(filepath=filepath).first()
    is_new = existing is None

    if existing:
        if os.path.exists(existing.file.path):
            os.remove(existing.file.path)

        existing.file = f
        existing.filename = filename
        existing.git_tracked = True
        existing.save()
        file_obj = existing
    else:
        file_obj = UploadedFile.objects.create(
            file=f,
            filename=filename,
            filepath=filepath,
            git_tracked=True
        )

    file_path = os.path.join(settings.MEDIA_ROOT, file_obj.file.name)

    try:
        subprocess.run(['git', 'add', file_path], check=True, cwd=REPO_ROOT)
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True, cwd=REPO_ROOT)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True, cwd=REPO_ROOT)

        commit_hash = get_latest_commit_hash()
        version_number = GitVersion.objects.filter(uploaded_file=file_obj).count() + 1

        GitVersion.objects.create(
            uploaded_file=file_obj,
            version_number=version_number,
            commit_hash=commit_hash,
            commit_message=commit_msg,
            author_name=username,
            committed_at=now(),
            branch_name='main'
        )

        GitActionLog.objects.create(
            action_type='PUSH',
            commit_hash=commit_hash,
            message=commit_msg,
            performed_by=username,
            target_branch='main'
        )

    except subprocess.CalledProcessError as e:
        print("Git 처리 중 오류:", e)

# Git 연동 파일 삭제 및 Git 커밋/푸시 처리
# - Git rm, commit, push 수행
# - GitActionLog에 기록
def delete_and_commit_file(file_obj, username):
    file_path = os.path.join(settings.MEDIA_ROOT, file_obj.file.name)
    filename = file_obj.filename

    try:
        subprocess.run(['git', 'rm', file_path], check=True, cwd=REPO_ROOT)
        subprocess.run(['git', 'commit', '-m', f"{filename} 삭제됨"], check=True, cwd=REPO_ROOT)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True, cwd=REPO_ROOT)

        commit_hash = get_latest_commit_hash()

        GitActionLog.objects.create(
            action_type='PUSH',
            commit_hash=commit_hash,
            message=f"{filename} 삭제됨",
            performed_by=username,
            target_branch='main'
        )

    except subprocess.CalledProcessError as e:
        print("Git 삭제 중 오류:", e)

# Git undo 기능: main 브랜치로 checkout
# - Git checkout main 수행
# - GitActionLog에 기록
def undo_checkout(username):
    try:
        subprocess.run(['git', 'checkout', 'main'], check=True, cwd=REPO_ROOT)
        GitActionLog.objects.create(
            action_type='UNDO',
            commit_hash=None,
            message="Undo checkout",
            performed_by=username,
            target_branch='main'
        )
    except subprocess.CalledProcessError as e:
        print("Undo 오류:", e)

# 특정 커밋 해시로 checkout 수행
# - Git checkout [commit_hash] 수행
# - GitActionLog에 기록
def checkout_commit(commit_hash, username):
    try:
        subprocess.run(['git', 'checkout', commit_hash], check=True, cwd=REPO_ROOT)
        GitActionLog.objects.create(
            action_type='CHECKOUT',
            commit_hash=commit_hash,
            message=f"Checkout to commit",
            performed_by=username,
            target_branch='main'
        )
    except subprocess.CalledProcessError as e:
        print("Checkout 오류:", e)

# 최근 N개 커밋을 squash 처리
# - Git soft reset 후 commit, force push 수행
# - GitActionLog에 기록
def squash_commits(n, username):
    try:
        subprocess.run(['git', 'reset', '--soft', f'HEAD~{n}'], check=True, cwd=REPO_ROOT)
        msg = f"Squashed last {n} commits"
        subprocess.run(['git', 'commit', '-m', msg], check=True, cwd=REPO_ROOT)
        subprocess.run(['git', 'push', '--force'], check=True, cwd=REPO_ROOT)

        commit_hash = get_latest_commit_hash()

        GitActionLog.objects.create(
            action_type='SQUASH',
            commit_hash=commit_hash,
            message=msg,
            performed_by=username,
            target_branch='main'
        )
    except subprocess.CalledProcessError as e:
        print("Squash 오류:", e)
