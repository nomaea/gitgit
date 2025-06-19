from django.db import models
from django.contrib.auth import get_user_model
from mptt.models import MPTTModel, TreeForeignKey

User = get_user_model()

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.user}"


class Comment(MPTTModel):  # MPTTModel을 상속받아 대댓글 구조 지원
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')  # 대댓글
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)  # 추후 soft-delete 확장 대비

    class MPTTMeta:
        order_insertion_by = ['created_at']

    def __str__(self):
        return f"Comment by {self.user} on {self.feedback}"
