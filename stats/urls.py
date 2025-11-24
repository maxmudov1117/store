from django.urls import path
from stats.views import *


urlpatterns = [
    path('sales/', SaleView.as_view(), name='sales'),
    path('sales/<int:pk>/update/', EditSalaView.as_view(), name="edit-sale"),
    path('imports/', ImportProductView.as_view(), name='imports'),
    path('import/<int:pk>/update', EditImportProductView.as_view(), name='edit-imports'),
    path('imports/<int:pk>/delete/confirm', DeleteImportProductView.as_view(), name='delete-imports'),
    path('pay-debt/', PaydebtView.as_view(), name='pay-debts'),
    path('pay-debt/<int:pk>/update/', EditPayDebtView.as_view(), name='edit-pay-debts'),
    path('pay-debt/<int:pk>/delete/confirm/', DeletePayDebtView.as_view(),name='delete-pay-debt')
]