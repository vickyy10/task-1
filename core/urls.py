
from django.urls import path,include
from . import views


urlpatterns = [
    # Dashboard
    path('login/', views.login_view, name='login'),
    path('', views.login_view, name='login'),
    path("logout/", views.logout_view, name="logout"),
    path('user/dashboard', views.user_dashboard, name='user_dashboard'),
    path('superadmin/dashboard/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # User management 
    path('users/', views.user_list, name='user_list'),
    path('admin-list/', views.admin_list, name='admin_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:user_id>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    path('admins/<int:user_id>/toggle-active/', views.admin_toggle_active, name='admin_toggle_active'),
     path('user/<int:user_id>/', views.user_detail, name='user_detail'),
    
    # Task management
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:task_id>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:task_id>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('update-task-status/', views.update_task_status, name='task_update_status'),

    
    # Reports
    path('reports/', views.reports, name='reports'),
]