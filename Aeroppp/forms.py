from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Manager, Engineer, Task, EngineerTask, EngineerManager, Document
from django.core.validators import MinValueValidator, MaxValueValidator



class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('engineer', 'Engineer'),
    ]
   
    first_name = forms.CharField(max_length = 50, required = True, widget = forms.TextInput(attrs = {'class':'form-control'}))
    last_name = forms.CharField(max_length = 50, required = True, widget = forms.TextInput(attrs = {'class':'form-control'}))
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, widget = forms.TextInput(attrs = {'class':'form-control'}))
    specialization = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs = {'class':'form-control'}))
    experience = forms.IntegerField(required=True, widget = forms.TextInput(attrs = {'class':'form-control'}))
    
    #manager_assigned = forms.ModelChoiceField(queryset=Manager.objects.all(), required=False)
    
    managers = forms.ModelMultipleChoiceField(queryset=Manager.objects.all(), required=False, widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    engineers = forms.ModelMultipleChoiceField(queryset = Engineer.objects.all(), required = False, widget = forms.SelectMultiple(attrs = {'class': 'form-control'}))

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role', 'specialization', 'experience', 'managers', 'engineers')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['experience'].required = True
        
        # Override managers field display based on selected role
        if 'role' in self.data:
            if self.data['role'] == 'manager':
                self.fields['managers'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        if role == 'manager':
            # If the role is manager, remove the managers field from cleaned_data
            cleaned_data.pop('managers', None)
        return cleaned_data
        


#class EngineerTaskForm(forms.ModelForm):
 #   def __init__(self, manager, *args, **kwargs):
  #      super().__init__(*args, **kwargs)
   #     self.fields['engineers'].queryset = Engineer.objects.filter(engineermanager__manager=manager)

   # engineers = forms.ModelMultipleChoiceField(queryset=Engineer.objects.none(), required=True)

   # class Meta:
   #     model = EngineerTask
   #     fields = ['engineers']
  
class EngineerTaskForm(forms.ModelForm):
    def __init__(self, manager=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if manager:
            self.fields['engineers'].queryset = Engineer.objects.filter(engineermanager__manager=manager)

    engineers = forms.ModelMultipleChoiceField(
        queryset=Engineer.objects.all(), 
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'engineer-checkbox'}),
    )


    class Meta:
        model = Engineer
        fields = ['engineers']
        widgets = {
            'name' : '10.0',
        }
        
   

    def __init__(self, *args, **kwargs):
        manager = kwargs.pop('manager', None)
        super().__init__(*args, **kwargs)
        if manager:
            queryset = Engineer.objects.filter(engineermanager__manager=manager)
            self.fields['engineers'].queryset = queryset
      

    def label_from_instance(self, obj):
        return (f"{obj.user.username} - {obj.specialization} - Experience: {obj.experience} - Rating: {obj.rating}")
    
        
class TaskForm(forms.ModelForm):
    
    #engineers = forms.ModelMultipleChoiceField(queryset=Engineer.objects.all(), required=True)
    
   # def __init__(self, *args, manager=None, **kwargs):
    #    super().__init__(*args, **kwargs)
     #   if manager:
      #      self.fields['engineers'].queryset = Engineer.objects.filter(engineermanager__manager=manager)
    class Meta:
        model = Task
        fields = ['title', 'aircraft', 'description', 'priority', 'deadline', 'progress']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'aircraft': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'priority': forms.TextInput(attrs={'class': 'form-control'}),
            'deadline': forms.DateTimeInput(attrs = {'class': 'form-control', 'type': 'datetime-local'}),
            'progress': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
class TaskProgressForm(forms.ModelForm):
    progress = forms.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])

    class Meta:
        model = Task
        fields = ['progress']
    
    #engineers = forms.ModelMultipleChoiceField(queryset=Engineer.objects.all(), required=True)

   # def __init__(self, *args, **kwargs):
       #super().__init__(*args, **kwargs)
        #self.fields['engineers'].widget.attrs.update({'class': 'selectpicker', 'data-live-search': 'true'})

   # def __init__(self, *args, **kwargs):
    #    manager = kwargs.pop('manager', None)
    #    super().__init__(*args, **kwargs)
    #    if manager:
    #        self.fields['assigned_team'].queryset = Engineer.objects.filter(engineermanager_manager = manager)
            
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    
    
class UpdateUserForm(forms.ModelForm):
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email']
        exclude = ['password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        
        
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file']

class MessageForm(forms.Form):
    message = forms.CharField(max_length=100)
    
    
class AssignEngineersForm(forms.Form):
    engineers = forms.ModelMultipleChoiceField(queryset = Engineer.objects.none(), widget = forms.CheckboxSelectMultiple)
    
    def __init__(self, *args, **kwargs):
        manager = kwargs.pop('manager', None)
        available_engineers = kwargs.pop('available_engineers', None)
        super().__init__(*args, **kwargs)
        
        if available_engineers is not None:
            self.fields['engineers'].queryset = available_engineers
            
            
class RemoveEngineersForm(forms.Form):
    engineers = forms.ModelMultipleChoiceField(queryset=Engineer.objects.none(), widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        manager = kwargs.pop('manager', None)
        assigned_engineers = kwargs.pop('assigned_engineers', None)
        super().__init__(*args, **kwargs)
        self.fields['engineers'].queryset = assigned_engineers
        
#class RemoveEngineersForm2(forms.Form):
 #   def __init__(self, task_id, *args, **kwargs):
  #      super(RemoveEngineersForm2, self).__init__(*args, **kwargs)
   #     task_engineers = EngineerTask.objects.filter(task_id=task_id)
    #    self.fields['engineers'] = forms.ModelMultipleChoiceField(
     #       queryset=task_engineers,
      #      widget=forms.CheckboxSelectMultiple,
       #     required=False
        #)
        

class RemoveEngineersForm2(forms.Form):
    def __init__(self, *args, **kwargs):
        task_id = kwargs.pop('task_id')  # Extract task_id from kwargs
        super(RemoveEngineersForm2, self).__init__(*args, **kwargs)
        task_engineers = Engineer.objects.filter(engineertask__task_id=task_id)
        self.fields['engineers'] = forms.ModelMultipleChoiceField(
            queryset=task_engineers,
            widget=forms.CheckboxSelectMultiple,
            required=False
        )
        

class EngineerRatingForm(forms.ModelForm):
    class Meta:
        model = Engineer
        fields = ['rating']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10, 'step': 1}),
        }