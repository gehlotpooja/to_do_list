from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import EmailValidationOnForgotPassword
from .views import *


urlpatterns = [
    path("", index, name="index"),
    path("register/", register_request, name="register"),
    path("login/", login_request, name="login"),
    path("logout/", logout_request, name= "logout"),
    path("active_tasks/", active_tasks, name= "tasks"),
    path("completed_tasks/", completed_tasks, name= "completed_tasks"),
    path("add_new_task/", add_new_task, name= "add_task"),
    path('refresh_data/', refresh_data, name='refresh_data'),
    path('move_tasks/', move_tasks, name='move_tasks'),
    path('delete_task/', delete_task, name='delete_task'),
    # path('login/', auth_views.LoginView.as_view(template_name='to_do_app/login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(template_name='to_do_app/logout.html'), name='logout'),
    # Including a EmailValidationOnForgotPassword class from users/forms.py - That tells the user that the entered
    # email during password reset is not a registered email (Not present in the system).
    path('password-reset/', auth_views.PasswordResetView.as_view(
        form_class=EmailValidationOnForgotPassword, template_name='to_do_app/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='to_do_app/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='to_do_app/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='to_do_app/password_reset_complete.html'), name='password_reset_complete')
]