from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('bundles/', views.bundles, name='bundles'),
    path('results/', views.results, name='results'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard')

]
