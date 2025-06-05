import base64
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from accounts.github.commit import commit_file_to_branch  # ✅ GitHub 커밋 함수
from django.utils.text import slugify
from django.shortcuts import render, redirect, get_object_or_404
from .forms import FileUploadForm
from django.conf import settings
from django.http import FileResponse
from workspace.models import UploadedFile, FileLog, UploadLog
from accounts.github.history import get_commit_history
import os


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_and_commit_to_github(request):
    """
    ✅ Git 연동 업로드 구역에서 파일 업로드 → GitHub 저장소에 커밋 + 업로드 로그 DB 저장
    """
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return Response({'status': 'error', 'message': 'No file uploaded'}, status=400)

    group_name = request.POST.get('group_name')
    if not group_name:
        return Response({'status': 'error', 'message': 'group_name required'}, status=400)

    branch_name = request.POST.get('branch_name', 'main')
    commit_message = request.POST.get('commit_message', f"{uploaded_file.name} 업로드")

    try:
        # 파일 내용 디코딩 (텍스트 or 바이너리 모두 지원)
        file_content = uploaded_file.read().decode()  # 텍스트 파일 전용
    except UnicodeDecodeError:
        file_content = base64.b64encode(uploaded_file.read()).decode()  # 바이너리 파일 처리

    # ✅ GitHub 저장소에 커밋 요청
    result = commit_file_to_branch(
        group_name=group_name,
        user=request.user,
        file_path=uploaded_file.name,
        file_content=file_content,
        commit_message=commit_message,
        branch_name=branch_name
    )

    # ✅ 업로드 로그 DB 저장
    if result['status'] == 'success':
        sha = result['commit']['commit']['sha']
        UploadLog.objects.create(
            user=request.user,
            group_name=group_name,
            file_path=uploaded_file.name,
            commit_message=commit_message,
            commit_sha=sha,
            branch_name=branch_name
        )

    return JsonResponse(result)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_github_commit_history(request):
    """
    ✅ 특정 그룹 저장소의 브랜치 내 커밋 히스토리 조회 API
    """
    group_name = request.GET.get('group_name')
    if not group_name:
        return Response({'status': 'error', 'message': 'group_name required'}, status=400)

    branch_name = request.GET.get('branch_name', 'main')
    file_path = request.GET.get('file_path')  # 선택적으로 파일 경로 지정 가능

    result = get_commit_history(group_name, request.user, branch_name, file_path)
    return JsonResponse(result)

# 그룹 스페이스에 git 연동을 하지 않는 일반 파일 업로드
def upload_and_list(request):
    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('files') # 사용자가 업로드한 파일 목록 불러오기

        for f in uploaded_files:
            file = f,
            filename = f.name.split('/')[-1],
            filepath = f.name,

                # 동일 경로의 파일이 이미 존재하는 경우 덮어쓰기 처리
            existing = UploadedFile.objects.filter(filepath=filepath).first()
            if existing:
                # 기존 파일 로그 (덮어쓰기 대상)
                FileLog.objects.create(
                    filename=existing.filename,
                    filepath=existing.filepath,
                    action='OVERWRITTEN_REMOVED',
                    file=existing
                )

                # 실제 파일 삭제
                if os.path.exists(existing.file.path):
                    os.remove(existing.file.path)

                # 기존 객체에 새 파일 내용 반영
                existing.file = f
                existing.filename = filename
                existing.save()

                # 덮어쓰기 후 최종 파일 로그
                FileLog.objects.create(
                    filename=existing.filename,
                    filepath=existing.filepath,
                    action='OVERWRITTEN_SAVED',
                    file=existing
                )
            else:
                # 신규 업로드
                uploaded = UploadedFile.objects.create(
                    file=f,
                    filename=filename,
                    filepath=filepath
                )
                FileLog.objects.create(
                    filename=uploaded.filename,
                    filepath=uploaded.filepath,
                    action='UPLOAD',
                    file=uploaded
                )
        return redirect('upload_and_list')

    # 업로드된 모든 파일을 시간 순으로 정렬하여 템플릿에 전달
    files = UploadedFile.objects.all().order_by('-uploaded_at')
    return render(request, 'workspace/upload_and_list.html', {
        'files': files,
        'request': request
    })

def delete_file(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id)  # 특정 ID의 파일을 찾고 없으면 404
    file_path = os.path.join(settings.MEDIA_ROOT, file.file.name)   # 실제 파일 경로

    # 파일 삭제 로그 기록
    FileLog.objects.create(
        filename=file.filename,
        action='DELETE'
    )

    # DB에서 삭제
    file.delete()

    # 서버에서 실제 파일 삭제
    if os.path.exists(file_path):
        os.remove(file_path)

    return redirect('upload_and_list')

def download_file(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id)
    file_path = os.path.join(settings.MEDIA_ROOT, file.file.name)

    # ✅ 다운로드 로그 기록
    FileLog.objects.create(
        filename=file.filename,
        action='DOWNLOAD'
    )
    # 파일을 다운로드용으로 응답
    return FileResponse(open(file_path, 'rb'), as_attachment=True)

