from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment
from group4.models import Notification  # 알림 모델이 group4에 있다고 가정

@receiver(post_save, sender=Comment)
def notify_feedback_owner_on_comment(sender, instance, created, **kwargs):
    if created:
        feedback_owner = instance.feedback.user
        commenter = instance.user

        if feedback_owner != commenter:
            Notification.objects.create(
                user=feedback_owner,
                message=f"{commenter.username}님이 '{instance.feedback.title}'에 댓글을 남겼습니다."
            )
