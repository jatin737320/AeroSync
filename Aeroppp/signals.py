from django.db.models.signals import post_save
from django.dispatch import receiver
from . models import Task, EngineerTask, TaskNotification

@receiver(post_save, sender = Task)
def create_task_notifications(sender, instance, created, **kwargs):
    if created:
        
        assigned_tasks = EngineerTask.objects.filter(task = instance)
        
        for task_assignment in assigned_tasks:
            TaskNotification.objects.create(task = instance, engineer = task_assignment.engineer)

