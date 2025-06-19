from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Feedback, Comment

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'created_at')
    search_fields = ('title', 'user__username')


@admin.register(Comment)
class CommentAdmin(MPTTModelAdmin):
    list_display = ('id', 'user', 'feedback', 'content', 'parent', 'created_at')
    search_fields = ('content', 'user__username', 'feedback__title')
