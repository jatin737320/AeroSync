from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Manager, Engineer, EngineerManager, Task, EngineerTask, Document, ChatMessage, UserLoginStatus, TaskNotification
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_manager', 'is_engineer', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_manager', 'is_engineer'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_manager', 'is_engineer')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Manager)
admin.site.register(Engineer)
admin.site.register(EngineerManager)
admin.site.register(Task)
admin.site.register(EngineerTask)
admin.site.register(Document)
admin.site.register(ChatMessage)

admin.site.register(UserLoginStatus)
admin.site.register(TaskNotification)