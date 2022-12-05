from django.shortcuts import render
from django.shortcuts import render, redirect
from .forms import NewUserForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from .models import Task
from rest_framework import status
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.contrib.auth.forms import PasswordResetForm
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.core.mail import send_mail, BadHeaderError


def index(request):
    return render(request, 'to_do_app/index.html')


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            form.save()
            # login(request, user)
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
    if request.method == 'POST':
        post_data = request.POST
        task_name = post_data.get('task_title')
        user = request.user
        task_obj = Task.objects.create(task_title=task_name, author=user)
        task_json_string = model_to_dict(task_obj, fields=['id', 'task_title', 'author'])
        return JsonResponse(task_json_string)
    else:
        return HttpResponse("Request method is not GET.")


@csrf_exempt
@login_required
def refresh_data(request):
    '''Returns the updated data after every AJAX Call.'''
    if request.method == 'POST':
        # Getting the username of the User requested
        user = request.user
        # Converting the user's tasks to JSON format
        data = serializers.serialize("json", user.task_set.all())
        # Return the JSON string. Will work only if safe is set to 'False'
        print("data ", data)
        return JsonResponse(data, safe=False)
    else:
        return HttpResponse('Request Method is not POST.')


@csrf_exempt
@login_required
def move_tasks(request):
    ''' Function to move the tasks from Active Table to Complete Table'''
    if request.method == 'POST':
        # Gets the Task's ID from the checkbox that is clicked
        task_id = request.POST['task_id']
        # Gets the Task's Class name from the checkbox that is clicked
        task_class = request.POST['task_state']
        # If the Clicked Task is an Active Task - Move it from Active Table to Complete Table
        if 'mark_as_done' in task_class:
            # Select the Task whose id matches with task_id
            done_task = Task.objects.get(pk=task_id)
            print("**********done task ", done_task)
            # Update the 'is_checked' attribute to True. i.e, Mark as Done
            done_task.is_checked = True
            # if object in done_task:
            done_task.save()

        # If the Clicked Task is a Complete Task - Move it from Complete Table to Active Table
        else:
            # Select the task matching with the task_id
            undone_task = Task.objects.get(pk=task_id)
            print("**********undone task ", undone_task)
            # Update the 'is_checked' attribute to 'False' i.e, Mark as Undone
            undone_task.is_checked = False
            # Save the changes to the Database
            undone_task.save()

        return HttpResponse("Success!")
    else:
        return HttpResponse("Request method is not GET.")


@csrf_exempt
@login_required
def delete_task(request):
    '''Deletes a task from the Task Table.'''
    if request.method == 'POST':
        # Getting the task_id from AJAX
        task_id = request.POST['task_id']
        # Selecting the task with the given task_id
        del_task = Task.objects.get(id=task_id)
        # Deleting the task from the Table
        del_task.delete()
        print(f'Deleted the Task with ID: {task_id}')
        return HttpResponse("Deleted the Task")
    else:
        return HttpResponse("Request method is not POST.")

@csrf_exempt
@login_required
def delete_all_completed_tasks(request):
    '''Deletes all the Completed tasks from the Completed Table'''
    if request.method == 'POST':
        # Getting the Tasks that are Marked as Completed - i.e, Tasks that have is_checked == 1
        del_tasks = Task.objects.filter(is_checked=1)
        # Deleting the Completed Tasks
        del_tasks.delete()
        # print('Deleted all Completed Tasks')
        return HttpResponse("Successfully Deleted all Completed Tasks")
    else:
        return HttpResponse("Request is not POST.")

def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "to_do_app/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': '127.0.0.1:9000',
                        'site_name': 'Website Name',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'AWS_verified_email_address', [user.email], fail_silently=False)
                    except BadHeaderError:

                        return HttpResponse('Invalid header found.')

                    messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
                    return redirect("index")
            messages.error(request, 'An invalid email has been entered.')
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="to_do_app/password_reset.html",
                  context={"password_reset_form": password_reset_form})
