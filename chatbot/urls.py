from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chatbot_page, name='chatbot_page'),
    path('reply/', views.chatbot_reply, name='chatbot_reply'),
   
]
