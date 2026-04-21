from django.urls import path
from stats.views import *


urlpatterns = [
    path('sales/', SaleView.as_view(), name='sales'),
    path('sales/<int:pk>/update/', EditSalaView.as_view(), name="edit-sale"),
    path('sales/<int:pk>/delete/confirm/', DeleteSaleView.as_view(), name='delete-sale'),
    path('imports/', ImportProductView.as_view(), name='imports'),
    path('import/<int:pk>/update', EditImportProductView.as_view(), name='edit-imports'),
    path('imports/<int:pk>/delete/confirm', DeleteImportProductView.as_view(), name='delete-imports'),
    path('pay-debt/', PaydebtView.as_view(), name='pay-debts'),
    path('pay-debt/<int:pk>/update/', EditPayDebtView.as_view(), name='edit-pay-debts'),
    path('pay-debt/<int:pk>/delete/confirm/', DeletePayDebtView.as_view(), name='delete-pay-debt'),

    # Excel export
    path('export/products/', ExportProductsView.as_view(), name='export-products'),
    path('export/sales/', ExportSalesView.as_view(), name='export-sales'),
    path('export/clients/', ExportClientsView.as_view(), name='export-clients'),
    path('export/imports/', ExportImportsView.as_view(), name='export-imports'),
    path('export/pay-debts/', ExportPayDebtsView.as_view(), name='export-pay-debts'),
    path('sales/<int:pk>/invoice/', DownloadInvoiceView.as_view(), name='download-invoice'),
]