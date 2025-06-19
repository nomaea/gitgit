from rest_framework import serializers
from .models import Feedback, Comment
from mptt.templatetags.mptt_tags import cache_tree_children

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'


class RecursiveCommentSerializer(serializers.Serializer):
    """대댓글 트리 직렬화용"""
    def to_representation(self, value):
        serializer = CommentSerializer(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    children = RecursiveCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'feedback', 'content', 'parent', 'created_at', 'children']
        read_only_fields = ['user', 'created_at']
