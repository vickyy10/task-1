from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .api_views import *

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('task/list', TaskListView.as_view(), name='task-list'),
    path('task/<int:task_id>/update/', TaskDetailView.as_view(), name='task-detail'),
    path('task/<int:task_id>/report/', TaskReportView.as_view(), name='task-report'),
]