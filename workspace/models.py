from django.db import models
from django.contrib.auth  import get_user_model

User = get_user_model()

# 업로드 정보 받아오기
class UploadedFile(models.Model):

    file = models.FileField(upload_to='uploads/')
    filename = models.CharField(max_length=255)
    filepath = models.TextField(max_length=500)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.filepath

#파일에 대한 타입 정의
class FileLog(models.Model):
    ACTION_CHOICES = [
        ('UPLOAD', '업로드'),
        ('DOWNLOAD', '다운로드'),
        ('DELETE', '삭제'),
        ('OVERWRITTEN_REMOVED', '덮어쓰기를 통한 삭제'),
        ('OVERWRITTEN_SAVED', '덮어쓰기를 통한 저장'),
    ]

    file = models.ForeignKey(UploadedFile, on_delete=models.SET_NULL, null=True, blank=True)
    filename = models.CharField(max_length=255) #파일 이름 기록
    filepath = models.TextField()
    action = models.CharField(max_length=20, choices=ACTION_CHOICES) # 타입 기록
    timestamp = models.DateTimeField(auto_now_add=True) #시간 기록

    # DB에 보여지는 순서
    def __str__(self):
        return f"{self.action} - {self.filename} ({self.timestamp})"

# github에 커밋되는 파일 로그 기록    
class UploadLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group_name = models.CharField(max_length=100)
    file_path = models.CharField(max_length=255)
    commit_message = models.TextField()
    commit_sha = models.CharField(max_length=100)
    branch_name = models.CharField(max_length=100, default='main')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.group_name} | {self.file_path} | {self.commit_sha[:7]}"    