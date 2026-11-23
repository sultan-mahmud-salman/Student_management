from django.urls import path
from . import views
urlpatterns = [
path('', views.dashboard, name='dashboard'),
path('students/', views.student_list, name='student_list'),
path('students/add/', views.student_create, name='student_create'),
path('students/edit/<int:id>/', views.student_update, name='student_update'),
path('students/delete/<int:id>/', views.student_delete, name='student_delete'),
path('register/', views.register, name='register'),
path('profile/', views.profile, name='profile'),
]