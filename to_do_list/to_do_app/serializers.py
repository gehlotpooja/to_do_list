from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Task
        fields = ('id', 'task_title', 'is_checked', 'created_at', 'updated_at', 'author')