from django.shortcuts import render, redirect, get_object_or_404    #django 유틸리티 함수
from .forms import FileUploadForm
from django.conf import settings
from django.http import FileResponse
from .models import UploadedFile, FileLog
from .git_service import git_upload, delete_and_commit_file
import os

username = 'testuser'

# 파일 업로드 및 파일 목록 뷰
def upload_and_list(request):
    if request.method == 'POST':    # POST 요청(업로드 요청)이 들어왔을 때만 파일 저장 로직 실행
        uploaded_files = request.FILES.getlist('files') # 사용자가 업로드한 파일들 리스트 가져오기
        commit_msg = request.POST.get('message', '(커밋 메시지 없음)')
        git_tracked = 'git' in request.POST #git 연동 여부 판단

        for f in uploaded_files:
            filename=f.name.split('/')[-1] # 파일 경로의 마지막 부분만 잘라서 이름 추출
            filepath=f.name # 전체 파일 경로 저장

            #git 연동 파일은 git_service에서 처리
            if git_tracked:
                git_upload(
                    f=f,
                    filepath=filepath,
                    filename=filename,
                    commit_msg=commit_msg,
                    username=username
                )
                continue

            else:    
                existing = UploadedFile.objects.filter(filepath=filepath).first()   # DB에 같은 경로의 파일 존재 여부 검사 
            # 덮어쓰기 처리
            if existing:
                # 기존 파일 로그 기록(덮어쓰기 대상)
                FileLog.objects.create(
                    filename=existing.filename,
                    filepath=existing.filepath,
                    action='OVERWRITTEN_REMOVED',
                    file=existing
                )

                # 실제 서버내 파일 삭제
                if os.path.exists(existing.file.path):
                    os.remove(existing.file.path)

                # 기존 객체에 새 파일 내용 반영
                existing.file = f
                existing.filename = filename
                existing.save()

                # 덮어쓰기 한 파일 로그 기록
                FileLog.objects.create(
                    filename=existing.filename,
                    filepath=existing.filepath,
                    action='OVERWRITTEN_SAVED',
                    file=existing
                )
            else:
                # 신규 업로드 처리
                uploaded = UploadedFile.objects.create(
                    file=f,
                    filename=filename,
                    filepath=filepath,
                    git_tracked=False
                )
                FileLog.objects.create(
                    filename=uploaded.filename,
                    filepath=uploaded.filepath,
                    action='UPLOAD',
                    file=uploaded
                )
        return redirect('upload_and_list')

    
    files = UploadedFile.objects.all().order_by('-uploaded_at') # 업로드된 모든 파일을 시간 순으로 정렬하여 템플릿에 전달
    return render(request, 'workspace/upload_and_list.html', {  # 업로드 화면 렌더링 및 파일 목록 request
        'files': files,
        'request': request
    })

# 파일 삭제 처리
def delete_file(request, file_id):  # file_id 기준 처리
    file = get_object_or_404(UploadedFile, id=file_id)  # 만약 파일이 존재 하지 않으면 404 에러 페이지 반환
    file_path = os.path.join(settings.MEDIA_ROOT, file.file.name)   # 서버내 실제 파일 경로 구성
    filename = file.filename

    if not file.git_tracked:
        FileLog.objects.create(
            filename=file.filename,
            filepath=file.file.name,
            action='DELETE',
            file=file
        )
    else:
        delete_and_commit_file(file, username)

    # DB에서 해당 파일 레코드 삭제
    file.delete()

    # 서버에서 실제 파일 삭제
    if os.path.exists(file_path):
        os.remove(file_path)

    return redirect('upload_and_list')

# 파일 다운로드 처리
def download_file(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id)
    file_path = os.path.join(settings.MEDIA_ROOT, file.file.name)
    if not file.git_tracked:
        FileLog.objects.create(
            filename=file.filename,
            action='DOWNLOAD'
        )
    
    return FileResponse(open(file_path, 'rb'), as_attachment=True)  # 브라우저에게 파일을 다운로드로 제공하도록 요청
