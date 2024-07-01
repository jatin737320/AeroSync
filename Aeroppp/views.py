from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.http import JsonResponse
from .forms import CustomUserCreationForm, LoginForm, TaskForm, EngineerTaskForm, TaskProgressForm, UpdateUserForm, DocumentForm, MessageForm, AssignEngineersForm, RemoveEngineersForm, RemoveEngineersForm2, EngineerRatingForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Manager, Engineer, Task, EngineerManager, EngineerTask, Document, ChatMessage, UserLoginStatus, TaskNotification, TaskUpdateNotification, TaskProgressNotification
from django.contrib.auth import login as auth_login
import logging
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings



# Create your views here.

logger = logging.getLogger(__name__)
def register(request):
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role = form.cleaned_data.get('role')
            user.is_manager = role == 'manager'
            user.is_engineer = role == 'engineer'
            user.save()
            
            if role == 'manager':
                specialization = form.cleaned_data.get('specialization')
                experience = form.cleaned_data.get('experience')
                manager = Manager.objects.create(user=user, specialization=specialization, experience=experience)
                engineers = form.cleaned_data.get('engineers')
                for engineer in engineers:
                    EngineerManager.objects.create(engineer = engineer, manager = manager)
                    
                send_mail("Welcome Manager!", "Congratulations, you're account has been registered!", settings.DEFAULT_FROM_EMAIL, [user.email])
            # If registering as an engineer
            elif role == 'engineer':
                specialization = form.cleaned_data.get('specialization')
                experience = form.cleaned_data.get('experience')
                #manager_assigned = form.cleaned_data.get('manager_assigned')
                engineer = Engineer.objects.create(user=user, specialization=specialization, experience=experience)
                managers = form.cleaned_data.get('managers')
                for manager in managers:
                    EngineerManager.objects.create(engineer = engineer, manager = manager)
                    
                send_mail("Welcome Engineer!", "Congratulations, you're account has been registered!", settings.DEFAULT_FROM_EMAIL, [user.email])
            
            #login(request, user)
            return redirect('login')
        
    managers = Manager.objects.all()
    engineers = Engineer.objects.all()
    context = {'RegistrationForm': form, 'Managers': managers, 'Engineers': engineers}
    return render(request, 'register.html', context)

@login_required(login_url = 'login')
def get_engineers(request):
    if not request.user.is_manager:
        return redirect('homepage')
    
    manager = request.user.manager
    
    assigned_engineers = Engineer.objects.filter(engineermanager__manager=manager)
    
    engineers = Engineer.objects.all()
    
    available_engineers = engineers.exclude(user_id__in=assigned_engineers.values_list('user_id', flat=True))
    #available_engineers = [engineer for engineer in  engineers if engineer not in assigned_engineers]
    form = AssignEngineersForm(manager = manager, available_engineers = available_engineers)
    
    if request.method == "POST":
        form = AssignEngineersForm(request.POST, manager = manager, available_engineers = available_engineers)
        
        if form.is_valid():
            selected_engineers = form.cleaned_data.get('engineers')
            for engineer in selected_engineers:
                EngineerManager.objects.create(engineer = engineer, manager = manager)
                
    
    context = {'Engineers': available_engineers , 'Form': form}
    
    return render(request, 'get-engineers.html', context)

@login_required(login_url = 'login')
def remove_engineers(request):
    if not request.user.is_manager:
        return redirect('homepage')
    
    manager = request.user.manager
    
    assigned_engineers = Engineer.objects.filter(engineermanager__manager = manager)
    
    form = RemoveEngineersForm(manager = manager, assigned_engineers = assigned_engineers)
    
    if request.method == "POST":
        form = RemoveEngineersForm(request.POST, manager = manager, assigned_engineers = assigned_engineers)
        
        if form.is_valid():
            selected_engineers = form.cleaned_data.get('engineers')
            
            
            
            for engineer in selected_engineers:
                engineer_tasks = EngineerTask.objects.filter(engineer=engineer)
                engineers_ = [task.task.created_by for task in engineer_tasks]
                if request.user in engineers_:
                    messages.error(request, f"Tasks are assigned to {engineer.user.get_full_name()}. Cannot be deleted.")

                    continue
                
                EngineerManager.objects.filter(manager = manager, engineer = engineer).delete()
                
    
    context = {'Engineers': assigned_engineers, 'Form': form}
    
    return render(request, 'delete-engineers.html', context)
    


@login_required(login_url = 'login')
def remove_teams(request, pk):
    
    if not request.user.is_manager:
        return redirect('homepage')
    
    task = Task.objects.get(id=pk, created_by=request.user)
    
    engineers_assigned = EngineerTask.objects.filter(task = task)
    
    engineer_ = []
    
    for engineer in engineers_assigned:
        engineer_.append(Engineer.objects.get(user = engineer.engineer))
        
    form = RemoveEngineersForm2(task_id = pk)
    
    if request.method == "POST":
        form = RemoveEngineersForm2(request.POST, task_id = pk)
        
        if form.is_valid():
            
            selected_engineers = form.cleaned_data.get('engineers')
            
            for engineer in selected_engineers:
                
                engineer_task = EngineerTask.objects.get(engineer = engineer, task = task)
                engineer_task.delete()
                
            engineers_assigned = EngineerTask.objects.filter(task=task)
            engineer_ = [engineer.engineer for engineer in engineers_assigned]
            
    
    form = RemoveEngineersForm2(task_id = pk)
                
    context = {'Form': form, 'Task': task, 'Engineers': engineer_}
    
    return render(request, 'remove-teams.html', context)
    
@login_required(login_url = 'login')         
def add_teams(request, pk):
    
    task = Task.objects.get(id=pk, created_by=request.user)
    manager = request.user.manager
    
    #assigned_engineers = Engineer.objects.filter(engineermanager__manager=manager)
    assigned_engineers = Engineer.objects.filter(engineermanager__manager=manager).exclude(engineertask__task=task)
    
    form = AssignEngineersForm(manager = manager, available_engineers = assigned_engineers)
    
    if request.method == "POST":
        
        form = AssignEngineersForm(request.POST, manager = manager, available_engineers = assigned_engineers)
        
        if form.is_valid():
            selected_engineers = form.cleaned_data.get('engineers')
            for engineer in selected_engineers:
                
                EngineerTask.objects.create(engineer = engineer, task = task)
                
        assigned_engineers = Engineer.objects.filter(engineermanager__manager=manager).exclude(engineertask__task=task)
        form = AssignEngineersForm(manager=manager, available_engineers=assigned_engineers)
        
    context = {'Form': form, 'Task': task, 'Engineers': assigned_engineers}
    
    return render(request, 'add-teams.html', context)


@login_required(login_url = 'login')
def edit_teams(request):
    if not request.user.is_manager:   
        return redirect('homepage')
    
    tasks = Task.objects.filter(created_by = request.user)
        
    manager_name = request.user.get_full_name()
    def truncate_description(description, word_limit = 5):
        words = description.split()
        
        if (len(words) > word_limit):
            return ' '.join(words[:word_limit])+'...'
        return description
    
    for task in tasks:
        task.truncated_description = truncate_description(task.description)
        
    
    context = {"Tasks" : tasks, "Manager": manager_name}
    
    return render(request, 'edit-teams.html', context)
    
        
            
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                # Redirect based on user's role
                UserLoginStatus.objects.update_or_create(user=user, defaults={'is_logged_in': True})
                
                if user.is_manager:
                    return redirect('manager-dashboard')
                elif user.is_engineer:
                    return redirect('engineer-dashboard')
                else:
                    # Redirect to a default homepage or dashboard
                    return redirect('homepage')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'LoginForm': form})

@login_required(login_url = 'login')
def create_task(request):
    if not request.user.is_manager:
        return redirect('homepage')
    
    #engineers = EngineerManager.objects.filter(manager = request.user.is_manager)
    
    manager = Manager.objects.get(user=request.user)
    engineers_ = Engineer.objects.filter(engineermanager__manager=manager)
    form = TaskForm()
    engineer_task_form = EngineerTaskForm(manager=manager)
   
    #engineers = Engineer.all()
    #engineers = request.user.manager.engineers.all()
    if request.method == "POST":
        form = TaskForm(request.POST)
        engineer_task_form = EngineerTaskForm(request.POST, manager=manager)
        if form.is_valid() and engineer_task_form.is_valid():
            task = form.save(commit = False)
            task.created_by = request.user
            task.save()
            
            #selected_engineers = form.cleaned_data['engineers']
            selected_engineers = engineer_task_form.cleaned_data['engineers']
           
            for engineer in selected_engineers:
                engineer_task = EngineerTask.objects.create(engineer=engineer, task = task)
                TaskNotification.objects.create(task = task, engineer = engineer.user)
                engineer_task.availability += 1
                engineer_task.save()
            
            return redirect('manager-dashboard')
    
        
    return render(request, 'create-task.html', {'form': form, 'engineer_task_form': engineer_task_form, 'engineers_': engineers_})

@login_required(login_url = 'login')
def update_task(request, pk):
    try:
        task = Task.objects.get(id=pk, created_by=request.user)
    except Task.DoesNotExist:
        return redirect('manager-dashboard')

    # Ensure only the manager who created the task can update it
    if not request.user.is_manager or task.created_by != request.user:
        return redirect('manager-dashboard')

    manager = Manager.objects.get(user=request.user)
    
    assigned_engineers = Engineer.objects.filter(engineermanager__manager = manager)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        

        if form.is_valid():
            task = form.save(commit=False)
            task.save()

            for engineer in assigned_engineers:
                TaskUpdateNotification.objects.create(task = task, engineer = engineer.user)
            messages.success(request, 'Task updated successfully')
            return redirect('manager-dashboard')
    else:
        form = TaskForm(instance=task)


    context = {'UpdateForm': form}
    

    return render(request, 'update-task.html', context)

@login_required(login_url = 'login')
def manager_dashboard(request):
    if request.user.is_authenticated and request.user.is_manager:
        if not request.user.is_manager:
            return redirect('homepage')
        
        tasks = Task.objects.filter(created_by = request.user)
        
        manager_name = request.user.get_full_name()
        def truncate_description(description, word_limit = 5):
            words = description.split()
            
            if (len(words) > word_limit):
                return ' '.join(words[:word_limit])+'...'
            return description
        
        for task in tasks:
            task.truncated_description = truncate_description(task.description)
            
        notifs_progress = TaskProgressNotification.objects.filter(user = request.user, read = False).count()
        
        context = {"Tasks" : tasks, "Manager": manager_name, 'Notifs': notifs_progress}
        
        return render(request, 'manager-dashboard.html', context)
    
    return redirect('login')

@login_required(login_url = 'login')
def view_task_manager(request, pk):
    if request.user.is_authenticated and request.user.is_manager:
        task = get_object_or_404(Task, id = pk)
        engineers = EngineerTask.objects.filter(task = task).values_list('engineer__user__first_name', 'engineer__user__last_name')
        engineer_names = [f"{first_name} {last_name}" for first_name, last_name in engineers]
        return render(request, 'view-task-manager.html', {'task': task, 'engineer_names': engineer_names})
    return redirect('login')
    
def homepage(request):
    return render(request, 'homepage.html')

# def manager_dashboard(request):
 #   return render(request, 'manager-dashboard.html')
@login_required(login_url = 'login')
def engineer_dashboard(request):
    if request.user.is_authenticated and request.user.is_engineer:
        if not request.user.is_engineer:
            redirect('homepage')
        
        engineer_tasks = EngineerTask.objects.filter(engineer = request.user.engineer)
        
        tasks = [(engineer_task.task, engineer_task.task.created_by.get_full_name()) for engineer_task in engineer_tasks]
        
        engineer_name = request.user.get_full_name()
        
        def truncate_description(description, word_limit = 5):
            words = description.split()
            
            if (len(words) > word_limit):
                return ' '.join(words[:word_limit])+'...'
            return description
        
        for task , manager in tasks:
            task.truncated_description = truncate_description(task.description)
            
        
        notifs_create = TaskNotification.objects.filter(engineer = request.user, read = False).count()
        
        notifs_update = TaskUpdateNotification.objects.filter(engineer = request.user, read = False).count()
          
        notifs_progress = TaskProgressNotification.objects.filter(user = request.user, read = False).count()
    
        context = {"Tasks" : tasks, 'engineer': engineer_name, 'Notifs': notifs_progress, 'Task_Notfis': notifs_create, 'Update_Notifs': notifs_update}
        
        
        return render(request, 'engineer-dashboard.html', context)


    return redirect('login')

@login_required(login_url = 'login')
def view_task_engineer(request, pk):
    if request.user.is_authenticated and request.user.is_engineer:
        task = get_object_or_404(Task, id = pk)
        manager_name = task.created_by.get_full_name()
        engineers = EngineerTask.objects.filter(task = task).values_list('engineer__user__first_name', 'engineer__user__last_name')
        engineer_names = [f"{first_name} {last_name}" for first_name, last_name in engineers]
        return render(request, 'view-task-engineer.html', {'task': task, 'engineer_names': engineer_names, 'manager': manager_name})

    return redirect('login')

@login_required(login_url = 'login')
def update_progress(request, pk):
    task = get_object_or_404(Task, id = pk)
    
    
    if request.user.is_manager:
        
        manager = Manager.objects.get(user = request.user)
        
        assigned_engineers = Engineer.objects.filter(engineermanager__manager = manager)
        
        
    elif request.user.is_engineer:
        
        assigned_engineers = EngineerTask.objects.filter(task = task)
        
        #manager_ = EngineerManager.objects.get(engineer = request.user.engineer)
        
        manager_ = task.created_by

    form = TaskProgressForm(instance = task)
    if request.method == "POST":
        form = TaskProgressForm(request.POST, instance = task)
        if form.is_valid():
            progress = form.cleaned_data['progress']
            
            task.progress = progress
            
            task.save()
            
            if request.user.is_engineer:
                TaskProgressNotification.objects.create(user = manager_, task = task, engineer = request.user.engineer, manager = None)
                for user in assigned_engineers:
                    TaskProgressNotification.objects.create(user = user.engineer.user, task = task, engineer = request.user.engineer, manager = None)
                    
            elif request.user.is_manager:
                TaskProgressNotification.objects.create(user = manager.user, task = task, manager = manager, engineer = None)
                for engineer in assigned_engineers:
                    TaskProgressNotification.objects.create(user = engineer.user, task = task, manager = request.user.manager, engineer = None)
            
            if request.user.is_manager:
                return redirect(reverse('view-task-manager', kwargs={'pk': pk}))
            elif request.user.is_engineer:
                return redirect(reverse('view-task-engineer', kwargs={'pk': pk}))
    
    context = {'Form': form}
    
    if request.user.is_manager:
        return render(request, 'update-task-progress-manager.html', context)
    elif request.user.is_engineer:
        return render(request, 'update-task-progress.html', context)

    
@login_required(login_url = 'login')     
def delete_task(request, pk):
    try:
        task = Task.objects.get(id=pk, created_by=request.user)
    except Task.DoesNotExist:
        return redirect('manager-dashboard')
    
    if request.method == "POST":
        
        task.delete()
        
        return redirect('manager-dashboard')
    
    return render(request, 'delete-task.html')


@login_required(login_url = 'login')
def assign_rating(request):
    if not request.user.is_manager:
        return redirect('login')
    
    manager = request.user.manager
    
    assigned_engineers = Engineer.objects.filter(engineermanager__manager = manager)
    
    forms = [EngineerRatingForm(instance=engineer, prefix=str(engineer.user.id)) for engineer in assigned_engineers]
    
    if request.method == "POST":
        all_valid = True
        
        for engineer in assigned_engineers:
            form = EngineerRatingForm(request.POST, instance=engineer, prefix=str(engineer.user.id))
            
            if form.is_valid():
                form.save()
            else:
                all_valid = False
        
        if all_valid:
            return redirect('manager-dashboard')
    
    #forms = [EngineerRatingForm(instance = engineer) for engineer in assigned_engineers]

    #if request.method == "POST":
        
        #for engineer in assigned_engineers:
        #    form = EngineerRatingForm(request.POST, instance = engineer)
            
        #    if form.is_valid():
        #        form.save()
                    
            
        #return redirect('manager-dashboard')
        
    
    #if request.method == "POST":
    #    forms = []
        
    #    for engineer in assigned_engineers:
    #        form = EngineerRatingForm(request.POST, instance = engineer)
            
    #        if (form.is_valid()):
    #            form.save()
    #            forms.append(form)
            
    #    return redirect('manager-dashboard')
    
    context = {'Manager': manager, 'Engineers': assigned_engineers, 'Forms': forms}
    return render(request, 'assign-ratings.html', context)

def view_notifications_tasks(request):
    engineer = request.user
    notifications = None
    notifications = TaskNotification.objects.filter(engineer = engineer, read = False)
    
    for notification in notifications:
        notification.read = True
        notification.save()
        
    context = {'Notifications': notifications}
    
    return render(request, 'creation-notifications.html', context)

def update_notifications(request):
    engineer = request.user
    notifications = None
    notifications = TaskUpdateNotification.objects.filter(engineer = engineer, read = False)
    
    for notification in notifications:
        notification.read = True
        notification.save()
        
    context = {'Notifications': notifications}
    
    return render(request, 'update-notification.html', context)

def progress_notifications(request):
    
    user = request.user
    
    notifications = None
    
    notifications = TaskProgressNotification.objects.filter(user = user, read = False)
    
    notifs = TaskProgressNotification.objects.filter(user = user, read = False).count()
    
    for notification in notifications:
        notification.read = True
        notification.save()
        
    context = {'Notifications': notifications, 'Notifs': notifs}
    
    if request.user.is_manager:
        return render(request, 'progress-notifications-manager.html', context)
    elif request.user.is_engineer:
        return render(request, 'progress-notifications.html', context)





@login_required(login_url = 'login')
def profile_management(request):
    
    form = UpdateUserForm(instance = request.user)
    
    if request.method == "POST":
        
        form = UpdateUserForm(request.POST, instance = request.user)
        
        if (form.is_valid()):
            
            form.save()
            
            if request.user.is_manager:
                
                return redirect('manager-dashboard')
        
            elif request.user.is_engineer:
                
                return redirect('engineer-dashboard')
            
    context = {'UpdateUserProfile': form}
    
    if request.user.is_manager:
        return render(request, 'profile-management-manager.html', context)
    elif request.user.is_engineer:
        return render(request, 'profile-management-engineer.html', context)

@login_required(login_url = 'login')
def upload_document(request, pk):
    task = Task.objects.get(id = pk)
    
    task_id = task.id
    form = DocumentForm()
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        
        if form.is_valid():
            
            document = form.save(commit = False)
            document.task = task
            document.uploaded_by = request.user
            document.save()
            
            return redirect('upload-document', task_id)
        
    
    documents = Document.objects.filter(task = task)
    context = {'Task': task, 'Form': form, 'documents': documents}
    
    return render(request, 'upload-document.html', context)

@login_required(login_url = 'login')  
def view_document(request, pk):
    
    task = Task.objects.get(id = pk)
    
    documents = Document.objects.filter(task = task)
    
    task_id = task.id
    form = DocumentForm()
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        
        if form.is_valid():
            
            document = form.save(commit = False)
            document.task = task
            document.uploaded_by = request.user
            document.save()
            
            return redirect('view-document', task_id)
        
    
    context = {'Form': form, 'Task': task, 'documents': documents}
    
    return render(request, 'view-document.html', context)

@login_required(login_url = 'login')
def delete_document(request, pk):
    document = get_object_or_404(Document, id = pk)
    
    task_pk = document.task.id
    
    if request.user.is_manager:
        task_id = document.task.id
        document.delete()
        
        return redirect('upload-document', task_pk)


# def task_chat_room(request, task_id):
  #  task = get_object_or_404(Task, id=task_id)
   # messages = ChatMessage.objects.filter(task=task).order_by('timestamp')
    
   # context = {'task': task, 'messages': messages}
   # return render(request, 'chat-room.html', context)

@login_required(login_url = 'login')
def send_message(request, pk):
    if request.method == "POST":
        content = request.POST.get('message')
        sender = request.user
        task = Task.objects.get(id = pk)
        message = ChatMessage.objects.create(task = task, sender = sender, message = content)
        
        return JsonResponse({'status': 'success'})
    
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
@login_required(login_url = 'login')    
def fetch_messages(request, task_id):
    task = Task.objects.get(id = task_id)
    messages = ChatMessage.objects.filter(task = task).order_by('timestamp')
    
    def format_timestamp(timestamp):
        dt_object = timestamp.astimezone()  # Ensure the timestamp is timezone-aware
        return dt_object.strftime("%Y-%m-%d %H:%M:%S")
    
    data = [{
        'sender': message.sender.get_full_name(),
        'content': message.message,
        'task_id': task_id,  # Include the task ID in the response
        'time': format_timestamp(message.timestamp),
    } for message in messages]
    return JsonResponse(data, safe = False)

@login_required(login_url = 'login')
def chat_room(request, pk):
    task = get_object_or_404(Task, id=pk)
    messages = ChatMessage.objects.filter(task=task)
    form = MessageForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            content = form.cleaned_data['message']
            sender = request.user
            #task = Task.objects.get(id=pk)
            message = ChatMessage.objects.create(task=task, sender=sender, message=content)
            #messages = ChatMessage.objects.filter(task = task)
            if request.user.is_manager:
               return redirect('manager-chat', pk=pk)
            elif request.user.is_engineer:
               return redirect('engineer-chat', pk = pk)
        
        
    context = {'Task': task, 'Form': form, 'Messages': messages}
    
    if request.user.is_manager:
        return render(request, 'manager-chat.html', context)
    elif request.user.is_engineer:
        return render(request, 'engineer-chat.html', context)

@login_required(login_url = 'login')
def logout_view(request):
    if request.user.is_authenticated:
        UserLoginStatus.objects.filter(user = request.user).update(is_logged_in = False)
        logout(request)
    return redirect('homepage')


