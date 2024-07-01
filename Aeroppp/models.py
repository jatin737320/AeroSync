from django.db import models


# Create your models here.
# myapp/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from datetime import timedelta
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUserManager(BaseUserManager):#role
    def create_user(self, username, email, password=None, role = None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        if role == 'manager':
            user.is_manager = True
        elif role == 'engineer':
            user.is_engineer = True
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_manager', False)
        extra_fields.setdefault('is_engineer', False)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)
class CustomUser(AbstractUser):
    is_manager = models.BooleanField(default=False)
    is_engineer = models.BooleanField(default=False)
    
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.username



class UserLoginStatus(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    is_logged_in = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
    
class Manager(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    experience = models.IntegerField()
    specialization = models.CharField(max_length=100)
    num_engineers_assigned = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

class Engineer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    specialization = models.CharField(max_length=100)
    experience = models.IntegerField()
    rating = models.IntegerField(default = 0)
    availability = models.IntegerField(default = 0)
    
    #manager_assigned = models.ForeignKey(Manager, on_delete=models.SET_NULL, null=True, blank=True)
    #managers = models.ManyToManyField(Manager, through='EngineerManager', related_name = "assigned_engineers")
    
    

    def __str__(self):
        return self.user.username

    
class EngineerManager(models.Model):
    engineer = models.ForeignKey(Engineer, on_delete=models.CASCADE)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.engineer} - {self.manager}"
    

    
class Task(models.Model):
    title = models.CharField(max_length = 200)
    aircraft = models.CharField(max_length = 200)
    description = models.TextField()
    priority = models.CharField(max_length = 50)
    #assigned_team = models.ManyToMany(Engine timezone.now() + timedelta(days=30))
    deadline = models.DateTimeField(default = timezone.now() + timezone.timedelta(days=3))
    
    created_by = models.ForeignKey(CustomUser, on_delete = models.CASCADE, related_name = "created_tasks")
    created_at = models.DateTimeField(auto_now_add = True)
    progress = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    #assigned_team = models.ManyToManyField(CustomUser, related_name = "assigned_tasks")
    
    def __str__(self):
        return self.title
    
    
class EngineerTask(models.Model):
    engineer = models.ForeignKey(Engineer, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    availability = models.IntegerField(default=0)

    class Meta:
        unique_together = ('engineer', 'task')

    def __str__(self):
        return f"{self.engineer.user.username} - {self.task.title}"
    
class Document(models.Model):
    task = models.ForeignKey(Task, on_delete = models.CASCADE)
    uploaded_by = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    file = models.FileField(upload_to = 'documents/', null = True)
    uploaded_at = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return self.file.name
    
class ChatMessage(models.Model):
    task = models.ForeignKey(Task, on_delete = models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return f'{self.sender.username} - {self.task.title}'
    
class TaskNotification(models.Model):
    task = models.ForeignKey('Task', on_delete = models.CASCADE)
    engineer = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    read = models.BooleanField(default = False)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.task.title} - {self.engineer.username}"
    
class TaskUpdateNotification(models.Model):
    task = models.ForeignKey('Task', on_delete = models.CASCADE)
    engineer = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    read = models.BooleanField(default = False)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.task.title} - {self.engineer.username}"
    
class TaskProgressNotification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    task = models.ForeignKey(Task, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    read = models.BooleanField(default = False)
    manager = models.ForeignKey(Manager, on_delete = models.CASCADE, null = True, blank = True)
    engineer = models.ForeignKey(Engineer, on_delete = models.CASCADE, null = True, blank = True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.task.title}"
    
    
    