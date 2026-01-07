from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('bundles/', views.bundles, name='bundles'),
    path('results/', views.bundles, name='results'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),  # Built-in view

]
