from rest_framework import serializers
from .models import CustomUser, Task, TaskReport, AdminUserAssignment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class TaskReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskReport
        fields = '__all__'

class AdminUserAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUserAssignment
        fields = '__all__'

