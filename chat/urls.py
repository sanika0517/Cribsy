from django.urls import path
from . import views

urlpatterns = [
    path('', views.conversations, name='conversations'),
    path('<str:username>/', views.conversation_view, name='conversation'),
]
