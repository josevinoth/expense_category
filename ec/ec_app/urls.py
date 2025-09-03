from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_bank_statement, name='upload'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('signup/', views.signup_view, name='signup'),
]
