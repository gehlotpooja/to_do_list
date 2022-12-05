from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import EmailValidationOnForgotPassword
from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("register/", register_request, name="register"),
    path("login/", login_request, name="login"),
    path("logout/", logout_request, name="logout"),
    path("active_tasks/", active_tasks, name="tasks"),
    path("completed_tasks/", completed_tasks, name="completed_tasks"),
    path("add_new_task/", add_new_task, name="add_task"),
    path('refresh_data/', refresh_data, name='refresh_data'),
    path('move_tasks/', move_tasks, name='move_tasks'),
    path('update_task/', update_task, name='update_task'),
    path('delete_task/', delete_task, name='delete_task'),
    path('delete_all_completed_tasks/', delete_all_completed_tasks, name='delete_all_completed_tasks'),
    path("password_reset/", password_reset_request, name="password_reset"),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='to_do_app/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='to_do_app/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='to_do_app/password_reset_complete.html'), name='password_reset_complete')
]
