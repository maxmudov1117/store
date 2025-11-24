from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import ExpressionWrapper, F, FloatField
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from main.models import *


class HomeView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        return render(request, 'sections.html')


class ProductView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        products = Product.objects.filter(branch=request.user.branch).annotate(
            total=ExpressionWrapper(
                F('quantity') * F('price'),
                output_field=FloatField()
            )
        ).order_by('-total')

        context = {
            'products': products,
            'branch': request.user.branch,
        }

        return render(request, 'products.html', context=context)

    def post(self, request):
        if request.user is None:
            return redirect('products')

        Product.objects.create(
            name=request.POST.get('name'),
            brand=request.POST.get('brand'),
            price=request.POST.get('price'),
            quantity=request.POST.get('quantity'),
            unit=request.POST.get('unit'),
            branch=request.user.branch,
        )

        return redirect('products')


class EditProductView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk, branch=request.user.branch)
        context = {
            'product': product,
        }

        return render(request, 'product-update.html', context=context)

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk, branch=request.user.branch)
        product.name = request.POST.get('name')
        product.brand = request.POST.get('brand')
        product.quantity = request.POST.get('quantity')
        product.unit = request.POST.get('unit')
        product.price = request.POST.get('price')
        product.branch = request.user.branch
        product.save()
        return redirect('products')


class DeleteProductView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk, branch=request.user.branch)
        context = {
            'product': product,
        }
        return render(request, 'delete.html', context=context)

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk, branch=request.user.branch)
        product.delete()
        return redirect('products')


class ClientsView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        clients = Client.objects.filter(branch=request.user.branch)
        context = {
            'clients':clients,
        }
        return render(request, 'clients.html', context=context)

    def post(self, request):
        Client.objects.create(
            name = request.POST.get('name'),
            shop_name = request.POST.get('shop_name'),
            phone_number = request.POST.get('phone_number'),
            address = request.POST.get('address'),
            debt = request.POST.get('debt'),
            branch = request.user.branch,
        )

        return redirect('clients')

class EditClientView( LoginRequiredMixin, View):
    login_url = 'login'
    def get(self, request, pk):
        client = get_object_or_404(Client, pk=pk, branch=request.user.branch)
        context = {
            'client':client,
        }

        return render(request, 'edit-client.html', context=context)

    def post(self, request, pk):
        client = get_object_or_404(Client, pk=pk, branch=request.user.branch)
        client.name = request.POST.get('name')
        client.shop_name = request.POST.get('shop_name')
        client.address = request.POST.get('address')
        client.debt = request.POST.get('debt')
        client.branch = request.user.branch
        client.save()
        return redirect('clients')

class DeleteClientView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        client = get_object_or_404(Client, pk=pk, branch=request.user.branch)
        context = {
            'client': client,
        }
        return render(request, 'delete-client.html', context=context)

    def post(self, request, pk):
        client = get_object_or_404(Client, pk=pk, branch=request.user.branch)
        client.delete()
        return redirect('clients')