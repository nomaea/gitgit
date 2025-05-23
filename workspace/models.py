from django.db import models
import shortuuid

# 업로드 정보 받아오기
class UploadedFile(models.Model):
    id = models.CharField(  # shortuuid 기반 PK
        primary_key=True,
        max_length=22,
        default=shortuuid.uuid,
        editable=False
    )
    file = models.FileField(upload_to='uploads/')
    filename = models.CharField(max_length=255)
    filepath = models.TextField(max_length=500) #filepath를 기준으로 유일성 제약 조건 판단
    uploaded_at = models.DateTimeField(auto_now_add=True) #파일의 업로드 시간 기록용 필드
    git_tracked = models.BooleanField(default=False)

    def __str__(self):
        return self.filename

#파일에 대한 타입 정의
class FileLog(models.Model):
    ACTION_CHOICES = [
        ('UPLOAD', '업로드'),
        ('DOWNLOAD', '다운로드'),
        ('DELETE', '삭제'),
        ('OVERWRITTEN_REMOVED', '덮어쓰기를 통한 삭제'),
        ('OVERWRITTEN_SAVED', '덮어쓰기'),
    ]

    # DB에 기록
    file = models.ForeignKey(UploadedFile, on_delete=models.SET_NULL, null=True, blank=True)
    filename = models.CharField(max_length=255) #파일 이름 기록
    filepath = models.TextField()
    action = models.CharField(max_length=20, choices=ACTION_CHOICES) # 타입 기록
    timestamp = models.DateTimeField(auto_now_add=True) #시간 기록

    # DB에 보여지는 순서
    def __str__(self):
        return f"{self.action} - {self.filename} ({self.timestamp})"
# git 연동을 통한 업로드 파일 확인 모델   
class GitVersion(models.Model):
    uploaded_file = models.ForeignKey(  # ForeignKey로 다대일 관계 변경
        'UploadedFile',
        on_delete=models.CASCADE,
        related_name='git_versions'
    )
    version_number = models.PositiveIntegerField()  # 버전 번호 필드
    commit_hash = models.CharField(max_length=40, unique=True)
    commit_message = models.TextField()
    author_name = models.CharField(max_length=100)
    committed_at = models.DateTimeField()
    branch_name = models.CharField(max_length=100, default='main')

    def __str__(self):
        return f"{self.uploaded_file.filename} - v{self.version_number}"

# git 액션 로그 기록 모델
class GitActionLog(models.Model):
    ACTION_CHOICES = [
        ('PUSH', 'Push'),
        ('CHECKOUT', 'Checkout'),
        ('UNDO', 'Undo'),
        ('SQUASH', 'Squash'),
    ]

    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    commit_hash = models.CharField(max_length=40, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    performed_at = models.DateTimeField(auto_now_add=True)
    performed_by = models.CharField(max_length=100)  # 사용자 이름 또는 ID
    target_branch = models.CharField(max_length=100, default='main')

    def __str__(self):
        return f"{self.action_type} by {self.performed_by} at {self.performed_at.strftime('%Y-%m-%d %H:%M')}"