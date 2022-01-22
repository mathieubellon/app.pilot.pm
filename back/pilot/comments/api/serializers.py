from rest_framework import serializers

from pilot.comments.models import Comment


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        depth = 1
        fields = (
            'data',
            'edition_date',
            'id',
            'is_deleted',
            'comment_content'
        )
