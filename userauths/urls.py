from django.urls import path
from userauths import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup/', views.signup, name="signup"),
    path('signin/', views.signin, name="login"),
    path('login-ajax/', views.login_ajax, name="login-ajax"),
    path('signup-ajax/', views.signup_ajax, name="signup-ajax"),
    path('email-verify/', views.email_verify, name="email-verify"),
    path('signout/', views.signout, name="signout"),
    path('email-verification/<unique>/', views.verify, name="email-verification"),
    path('forgot-password/', views.reset_password, name="reset"),
    path('reset-password/<token>/', views.create_password, name="reset-password"),
    path('bulk-upload/', views.bulk, name="bulk"),
    path('bulk-added/', views.bulk_added, name="bulk_added"),
    path('email-sql/', views.backup_sqlite_to_brevo, name="backup_sqlite_to_brevo"),
    # path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    # path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]