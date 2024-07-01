from django.contrib import admin
from django.urls import path

from . import views

from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.homepage, name = "homepage"),
    path('register', views.register, name = "register"),
    path('login', views.login, name = "login"),
    path('manager-dashboard', views.manager_dashboard, name = "manager-dashboard"),
    path('engineer-dashboard', views.engineer_dashboard, name = "engineer-dashboard"),
    path('logout', views.logout_view, name = "logout"),
    path('create-task/', views.create_task, name = "create-task"),
    path('manager-tasks/<str:pk>', views.view_task_manager, name = "view-task-manager"),
    path('engineer-tasks/<str:pk>', views.view_task_engineer, name = "view-task-engineer"),
    path('update-task/<str:pk>', views.update_task, name = "update-task"),
    path('delete-task/<str:pk>', views.delete_task, name = "delete-task"),
    path('update-task-progress/<str:pk>', views.update_progress, name = "update-task-progress"),
    path('update-task-progress-manager/<str:pk>', views.update_progress, name = "update-task-progress-manager"),
    path('profile-management-manager', views.profile_management, name = "profile-management-manager"),
    path('profile-management-engineer', views.profile_management, name = "profile-management-engineer"),
    path('upload-document/<str:pk>', views.upload_document, name = "upload-document"),
    path('view-document/<str:pk>', views.view_document, name = "view-document"),
    path('delete-document/<str:pk>', views.delete_document, name = "delete-document"),
    #path('task/<str:task_id>/chat/', views.task_chat_room, name='chat-room'),
    path('send-message/<str:pk>', views.send_message, name = "send-message"),
    path('fetch-messages/<str:task_id>', views.fetch_messages, name = "fetch-messages"),
    path('manager-chat/<str:pk>', views.chat_room, name = "manager-chat"),
    path('engineer-chat/<str:pk>', views.chat_room, name = "engineer-chat"),
    path('get-engineers', views.get_engineers, name = "get-engineers"),
    path('delete-engineers', views.remove_engineers, name = "delete-engineers"),
    path('edit-teams', views.edit_teams, name = "edit-teams"),
    path('remove-teams/<str:pk>', views.remove_teams, name = "remove-teams"),
    path('add-teams/<str:pk>', views.add_teams, name = "add-teams"),
    path('assign-rating/', views.assign_rating, name = "assign-ratings"),
    path('creation-notification', views.view_notifications_tasks, name = 'creation-notifications'),
    path('update-notification', views.update_notifications, name = "update-notification"),
    path('progress-notifications', views.progress_notifications, name = "progress-notifications"),
    path('progress-notifications-manager', views.progress_notifications, name = "progress-notifications-manager"),
    
    #Password Management
    
    # 1- Allow us to enter our email to reset our password
    
    path('reset_password', auth_views.PasswordResetView.as_view(template_name = "password-reset.html"), name = "reset_password"),
    
    # 2- Show a success message showing that an email was sent.
    
    path('reset_password_sent', auth_views.PasswordResetDoneView.as_view(template_name = "password-reset-sent.html"), name = "password_reset_done"),
    
    # 3 - Send a link to our email, so that we can reset our password.
    
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name = "password-reset-form.html"), name = "password_reset_confirm"),
    
    # 4- Show a success message that our password was changed.

    path('password_reset_complete', auth_views.PasswordResetCompleteView.as_view(template_name = "password-reset-complete.html"), name = "password_reset_complete"),
    
]