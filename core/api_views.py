from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.contrib.auth import login
from .models import User, Task
from .serializers import UserSerializer, TaskSerializer, TaskCompletionSerializer, LoginSerializer



class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class TaskListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        tasks = Task.objects.filter(assigned_to=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    


class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, task_id, user):
        return get_object_or_404(Task, id=task_id, assigned_to=user)
    
    def put(self, request, task_id):
        task = self.get_object(task_id, request.user)
        
        if request.data.get('status') == 'completed':
            completion_serializer = TaskCompletionSerializer(task, data=request.data, partial=True)
            if completion_serializer.is_valid():
                completion_serializer.save(
                    status='completed',
                    completed_at=timezone.now()
                )
                serializer = TaskSerializer(task, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(completion_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                if serializer.validated_data.get('status') == 'in_progress' and not task.started_at:
                    serializer.save(started_at=timezone.now())
                else:
                    serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


class TaskReportView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, task_id):

        if not (request.user.is_admin or request.user.is_superadmin):
            return Response(
                {"error": "Only admin users can view task reports."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        task = get_object_or_404(Task, id=task_id)
        
        if task.status != 'completed':
            return Response(
                {"error": "Task is not completed yet."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.user.is_admin and not request.user.is_superadmin:
            if task.assigned_to.assigned_admin != request.user and task.created_by != request.user:
                return Response(
                    {"error": "You can only view reports for tasks assigned to your users."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = TaskSerializer(task)
        return Response({
            'completion_report': task.completion_report,
            'worked_hours': task.worked_hours,
            'task_details': serializer.data
        })
