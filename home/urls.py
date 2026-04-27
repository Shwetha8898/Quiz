from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
   path('', views.home , name = 'home'),
   path('quiz/', views.quiz, name= 'quiz'),
   path('api/get-quiz/', views.get_quiz, name='get_quiz'),
   path('score/', views.score, name='score'),
   path('login/', views.login_view, name='login'),
   path('register/', views.register_view, name='register'),
   path('logout/', views.logout_view, name='logout'),
   path('submit-quiz/', views.submit_quiz, name='submit_quiz'),
   path('profile/', views.profile, name='profile'),
   path('leaderboard/', views.leaderboard, name='leaderboard'),
]
