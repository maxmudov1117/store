from django.urls import path

from main.views import *

urlpatterns = [
    path('products/', ProductView.as_view(), name='products'),
    path('products/<int:pk>/update/', EditProductView.as_view(), name='edit-product'),
    path('products/<int:pk>/delete/confirm', DeleteProductView.as_view(), name='delete-product'),
    path('clients/', ClientsView.as_view(), name='clients'),
    path('clients/<int:pk>/update', EditClientView.as_view(), name='edit-client' ),
    path('clients/<int:pk>/delete/confirm', DeleteClientView.as_view(), name='delete-client'),
]