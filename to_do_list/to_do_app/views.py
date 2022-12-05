from django.shortcuts import render, redirect
from .forms import NewUserForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from .models import Task
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import PasswordResetForm
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from .serializers import TaskSerializer


def index(request):
    return render(request, 'to_do_app/index.html')


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            form.save()
            fname = form.cleaned_data.get('first_name')
            messages.add_message(
                request, messages.SUCCESS,
                f"Hey {fname}, Your account has been created successfully. You can login now.")
            messages.success(request, "Registration successful.")
            return redirect('login')
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="to_do_app/register.html", context={"register_form": form})


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('tasks')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="to_do_app/login.html", context={"login_form": form})


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(email=data)
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "to_do_app/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': '127.0.0.1:9000',
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'admin@example.com', [user.email], fail_silently=False)
                    except BadHeaderError:

                        return HttpResponse('Invalid header found.')

                    messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
                    return redirect("index")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="to_do_app/password_reset.html",
                  context={"password_reset_form": password_reset_form})


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('login')


def active_tasks(request):
    return render(request=request, template_name='to_do_app/activetasks.html')


def completed_tasks(request):
    return render(request=request, template_name='to_do_app/completedtasks.html')


@csrf_exempt
@login_required
def add_new_task(request):
    '''Adds a New Task to the Task Table in Database.'''
    ret_data = {
        'success': False,
        'msg': 'Error in saving task'
    }
    try:
        if request.method == 'POST':
            post_data = request.POST
            task_name = post_data.get('task_title')
            user = request.user
            Task.objects.create(task_title=task_name, author=user)
            ret_data['success'] = True
            ret_data['msg'] = 'Task successfully saved'
        else:
            ret_data['msg'] = 'Request method is not GET.'
    except Exception as e:
        print(e.args)
    return JsonResponse(ret_data)


@csrf_exempt
@login_required
def refresh_data(request):
    '''Returns the updated data after every AJAX Call.'''
    ret_data = {
        'success': False,
        'msg': 'Error in getting task data',
        'data': []
    }
    try:
        if request.method == 'POST':
            # Getting the user object of the User requested
            user = request.user
            task_obj = Task.objects.filter(author=user)
            serializer = TaskSerializer(task_obj, many=True)
            data = serializer.data
            ret_data['success'] = True
            ret_data['msg'] = 'Task successfully saved'
            ret_data['data'] = data
        else:
            ret_data['msg'] = 'Request Method is not POST.'
    except Exception as e:
        print(e.args)
    return JsonResponse(ret_data)



@csrf_exempt
@login_required
def move_tasks(request):
    ''' Function to move the tasks from Active Table to Complete Table'''
    ret_data = {
        'success': False,
        'msg': 'Error in moving task'
    }
    try:
        if request.method == 'POST':
            # Gets the Task's ID from the checkbox that is clicked
            task_id = request.POST['task_id']
            # Gets the Task's Class name from the checkbox that is clicked
            task_state = request.POST['task_state']
            if task_id and task_state:
                is_checked = False
                if task_state == 'true':
                    is_checked = True
                # If the Clicked Task is an Active Task - Move it from Active Table to Complete Table
                # Select the Task whose id matches with task_id
                done_task = Task.objects.get(pk=task_id)
                # Update the 'is_checked' attribute to True. i.e, Mark as Done
                done_task.is_checked = is_checked
                # if object in done_task:
                done_task.save()
                ret_data['success'] = True
                ret_data['msg'] = 'Task successfully moved'
            else:
                ret_data['msg'] = 'Required parameter not present. Please contact admin'
        else:
            ret_data['msg'] = 'Request Method is not GET.'
    except Exception as e:
        print(e.args)
    return JsonResponse(ret_data)

@csrf_exempt
@login_required
def delete_task(request):
    '''Deletes a task from the Task Table.'''
    ret_data = {
        'success': False,
        'msg': 'Error in Deleting task'
    }
    try:
        if request.method == 'POST':
            # Getting the task_id from AJAX
            task_id = request.POST['task_id']
            # Selecting the task with the given task_id
            Task.objects.filter(id=task_id).delete()
            # Deleting the task from the Table
            ret_data['success'] = True
            ret_data['msg'] = f'Deleted the Task with ID: {task_id}'
        else:
            ret_data['msg'] = 'Request Method is not POST.'
    except Exception as e:
        print(e.args)
    return JsonResponse(ret_data)


@csrf_exempt
@login_required
def delete_all_completed_tasks(request):
    '''Deletes all the Completed tasks from the Completed Table'''
    ret_data = {
        'success': False,
        'msg': 'Error in Deleting all task'
    }
    try:
        if request.method == 'POST':
            # Getting the Tasks that are Marked as Completed - i.e, Tasks that have is_checked == 1
            # Deleting the Completed Tasks
            Task.objects.filter(is_checked=1).delete()
            ret_data['success'] = True
            ret_data['msg'] = "Successfully Deleted all Completed Tasks"
        else:
            ret_data['msg'] = "Request is not POST."
    except Exception as e:
        print(e.args)
    return JsonResponse(ret_data)


@csrf_exempt
@login_required
def update_task(request):
    '''Updates the task'''
    ret_data = {
        'success': False,
        'msg': 'Error in updating task'
    }
    try:
        if request.method == 'POST':
            # Getting the Task ID of the task to be updated from AJAX Call
            task_id = request.POST['task_id']
            # Getting the modified Task name from AJAX Call
            new_task = request.POST['task_name']
            # Querying the Task model to get the task based on task_id
            changed_task = Task.objects.get(id=task_id)
            # Updating the Task Name with the NEW Value
            changed_task.task_title = new_task.strip()
            # Saving the changes to the Database
            changed_task.save()
            # For Debugging Purpose
            ret_data['success'] = True
            ret_data['msg'] = f'Successfully Task Updated ID: {task_id}'
        else:
            ret_data['msg'] = 'Request is not POST.'
    except Exception as e:
        print(e.args)
    return JsonResponse(ret_data)


