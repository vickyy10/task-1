from django.db import models
from.constants import ROLE_CHOICES,STATUS_CHOICES
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        help_text='User role in the system'
    )
    
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        help_text='User profile picture'
    )
    
    is_active = models.BooleanField(default=True)
    
    assigned_admin = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_users',
    )


    def __str__(self):
        return f"{self.username}"

    @property
    def is_user(self):
        return self.role == 'user'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_superadmin(self):
        return self.role == 'superadmin'

    def can_manage_user(self, user):
        """Check if this user can manage another user"""
        if self.is_superadmin:
            return True
        if self.is_admin and user.assigned_admin == self:
            return True
        return False
    


class Task(models.Model):

    title = models.CharField(max_length=200,help_text='Task title/name')
    description = models.TextField()
    assigned_to = models.ForeignKey(User,on_delete=models.CASCADE,related_name='assigned_tasks' )
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='created_tasks')
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField()
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the task was started'
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the task was completed'
    )
    completion_report = models.TextField(
        blank=True,
        null=True,
        help_text='Detailed report provided when task is completed'
    )
    worked_hours = models.DecimalField(max_digits=6,decimal_places=2,null=True,blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['assigned_to', 'status','due_date','created_by']),
        ]

    def __str__(self):
        return f"{self.title} - ({self.status})"
