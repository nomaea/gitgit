from django.urls import path
from . import views
from workspace.views import get_commit_history

urlpatterns = [
    path('', views.upload_and_list, name='upload_and_list'),    # 파일 업로드 및 목록 보기
    path('delete/<int:file_id>/', views.delete_file, name='delete_file'),   # 파일 삭제 요청
    path('download/<int:file_id>/', views.download_file, name='download_file'), # 파일 다운로드 요청
    path('git-commits/', views.get_github_commit_history, name='git_commit_history'), # 파일 히스토리 확인 요청
    path('git-upload/', views.upload_and_commit_to_github, name='upload_and_commit_to_github'), # git 연동 커밋 요청
]
