from django.urls import path
from . import views

urlpatterns = [
    # Page routes
    path('', views.index, name='index'),
    path('bundles/', views.bundles, name='bundles'),
    path('results/', views.results, name='results'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Auth routes
    path('sign-up/', views.sign_up, name='sign_up'),
    path('logout/', views.user_logout, name='logout'),

    # Upload API routes
    path('api/uploads/remaining/', views.get_uploads_remaining, name='api_uploads_remaining'),
    path('api/uploads/use/', views.use_upload, name='api_use_upload'),
    path('api/documents/submit/', views.submit_documents, name='api_submit_documents'),
    path('api/bundles/purchase/', views.purchase_bundle, name='api_purchase_bundle'),
]