from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_and_list, name='upload_and_list'),    # 파일 업로드 및 목록 보기
    path('delete/<str:file_id>/', views.delete_file, name='delete_file'),   # 파일 삭제 요청
    path('download/<str:file_id>/', views.download_file, name='download_file'), # 파일 다운로드 요청
]
