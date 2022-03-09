from django.urls import path

from . import views


urlpatterns = [
    path('login/', views.login_page, name="login"),
    path('logout/', views.logout_user, name="logout"),
    path('register/', views.register_page, name="register"),

    path('', views.home, name="home"),
    
    path('password-details/<int:pk>/', views.password_details, name="password-details"),

    path('create-password/', views.create_password, name="create-password"),
    path('update-password/<int:pk>', views.update_password, name="update-password"),
    path('delete-password/<int:pk>', views.delete_password, name="delete-password"),
]