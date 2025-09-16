from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Task


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'assigned_admin')



class TaskSerializer(serializers.ModelSerializer):
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)
    
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at', 'started_at', 'completed_at')

class TaskCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('completion_report', 'worked_hours')
        
    def validate(self, data):
        if not data.get('completion_report'):
            raise serializers.ValidationError("Completion report is required when marking task as completed.")
        if not data.get('worked_hours'):
            raise serializers.ValidationError("Worked hours is required when marking task as completed.")
        return data


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError("User account is disabled.")
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include username and password.")
            
        return data