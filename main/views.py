from django.shortcuts import render, redirect
from django.db.models import ExpressionWrapper, F, FloatField
from django.views import View
from main.models import *


class HomeView(View):
    def get(self, request):
        return render(request, 'sections.html')


class ProductView(View):
    def get(self, request):
        products = Product.objects.annotate(
            total=ExpressionWrapper(
                F('quantity') * F('price'),
                output_field=FloatField()
            )
        ).order_by('-total')

        context = {
            'products': products,
        }

        return render(request, 'products.html', context=context)

    def post(self, request):
        Product.objects.create(
            name=request.POST.get('name'),
            brand=request.POST.get('brand'),
            price=request.POST.get('price'),
            quantity=request.POST.get('quantity'),
            unit=request.POST.get('unit'),
            branch=Branch.objects.first()
        )

        return redirect('products')
