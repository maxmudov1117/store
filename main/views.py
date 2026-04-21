from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import json
from django.db.models import ExpressionWrapper, F, FloatField, Sum, Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.utils import timezone
from django.core.paginator import Paginator
from main.models import Product, Branch, Client

class HomeView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        branch = request.user.branch
        if not branch:
             return render(request, 'warning.html', {
                'warning_title': 'Filial biriktirilmagan',
                'warning_message': "Sizning hisobingizga filial biriktirilmagan.",
                'back_url': 'home'
            })

        # Dashboard statistics
        products = Product.objects.filter(branch=branch)
        clients = Client.objects.filter(branch=branch)
        today = timezone.now().date()

        # Import models here to avoid circular imports
        from stats.models import Sale

        today_sales = Sale.objects.filter(branch=branch, created_at=today)
        all_sales = Sale.objects.filter(branch=branch)
        recent_sales = all_sales.order_by('-created_at', '-id')[:5]

        # Calculations for modern dashboard
        today_sales_total = today_sales.aggregate(total=Sum('total_price'))['total'] or 0
        total_debt = clients.aggregate(total=Sum('debt'))['total'] or 0
        
        # Stock value calculation using 'price' as per model
        stock_value = products.aggregate(total=Sum(F('price') * F('quantity'), output_field=FloatField()))['total'] or 0

        # Chart Data (Last 30 days)
        chart_labels = []
        chart_data = []
        for i in range(29, -1, -1):
            date = today - timezone.timedelta(days=i)
            day_sales = all_sales.filter(created_at=date).aggregate(total=Sum('total_price'))['total'] or 0
            chart_labels.append(date.strftime('%d-%b'))
            chart_data.append(float(day_sales))

        context = {
            'total_products': products.count(),
            'total_clients': clients.count(),
            'today_sales_total': today_sales_total,
            'today_sales_count': today_sales.count(),
            'total_debt': total_debt,
            'stock_value': stock_value,
            'recent_sales': recent_sales,
            'chart_labels': json.dumps(chart_labels),
            'chart_data': json.dumps(chart_data),
            'branch': branch,
        }
        return render(request, 'sections.html', context=context)

class ProductsView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        products = Product.objects.filter(branch=request.user.branch)
        search = request.GET.get('search', '').strip()
        if search:
            products = products.filter(Q(name__icontains=search) | Q(brand__icontains=search))
        paginator = Paginator(products, 25)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'products.html', {'products': page_obj, 'page_obj': page_obj, 'search': search})

    def post(self, request):
        if not request.user.branch:
            return redirect('products')
        
        buy_price = float(request.POST.get('buy_price') or 0)
        quantity = float(request.POST.get('quantity') or 0)
        
        product = Product.objects.create(
            name=request.POST.get('name'),
            brand=request.POST.get('brand'),
            price=request.POST.get('price') or 0,
            quantity=quantity,
            unit=request.POST.get('unit'),
            branch=request.user.branch,
        )

        # Record the initial purchase price
        if buy_price > 0:
            from stats.models import ImportProduct
            ImportProduct.objects.create(
                product=product,
                buy_price=buy_price,
                quantity=quantity,
                branch=request.user.branch,
                user=request.user
            )

        return redirect('products')

class EditProductView(LoginRequiredMixin, View):
    login_url = 'login'
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk, branch=request.user.branch)
        return render(request, 'product-update.html', {'product': product})
    
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk, branch=request.user.branch)
        product.name = request.POST.get('name')
        product.brand = request.POST.get('brand')
        product.price = request.POST.get('price') or 0
        product.quantity = request.POST.get('quantity') or 0
        product.unit = request.POST.get('unit')
        product.save()
        return redirect('products')

class DeleteProductView(LoginRequiredMixin, View):
    login_url = 'login'
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk, branch=request.user.branch)
        return render(request, 'delete.html', {'product': product})
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk, branch=request.user.branch)
        product.delete()
        return redirect('products')

class ClientsView(LoginRequiredMixin, View):
    login_url = 'login'
    def get(self, request):
        clients = Client.objects.filter(branch=request.user.branch)
        search = request.GET.get('search', '').strip()
        if search:
            clients = clients.filter(Q(name__icontains=search) | Q(shop_name__icontains=search) | Q(phone_number__icontains=search))
        paginator = Paginator(clients, 25)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'clients.html', {'clients': page_obj, 'page_obj': page_obj, 'search': search})
    def post(self, request):
        if not request.user.branch:
            return redirect('clients')
        Client.objects.create(
            name=request.POST.get('name'),
            shop_name=request.POST.get('shop_name'),
            phone_number=request.POST.get('phone_number'),
            address=request.POST.get('address'),
            debt=request.POST.get('debt'),
            branch=request.user.branch,
        )
        return redirect('clients')

class EditClientView(LoginRequiredMixin, View):
    login_url = 'login'
    def get(self, request, pk):
        client = get_object_or_404(Client, pk=pk, branch=request.user.branch)
        return render(request, 'edit-client.html', {'client': client})
    def post(self, request, pk):
        client = get_object_or_404(Client, pk=pk, branch=request.user.branch)
        client.name = request.POST.get('name')
        client.shop_name = request.POST.get('shop_name')
        client.address = request.POST.get('address')
        client.debt = request.POST.get('debt')
        client.save()
        return redirect('clients')

class DeleteClientView(LoginRequiredMixin, View):
    login_url = 'login'
    def get(self, request, pk):
        client = get_object_or_404(Client, pk=pk, branch=request.user.branch)
        return render(request, 'delete-client.html', {'client': client})
    def post(self, request, pk):
        client = get_object_or_404(Client, pk=pk, branch=request.user.branch)
        client.delete()
        return redirect('clients')

class BranchView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = 'login'
    def test_func(self):
        return self.request.user.is_superuser
    def get(self, request):
        branches = Branch.objects.all().order_by('-created_at')
        return render(request, 'branches.html', {'branches': branches})
    def post(self, request):
        if not self.request.user.is_superuser:
            return redirect('home')
        branch_id = request.POST.get('branch_id')
        name = request.POST.get('name')
        info = request.POST.get('info')
        if branch_id:
            branch = get_object_or_404(Branch, id=branch_id)
            branch.name = name
            branch.info = info
            branch.save()
        else:
            Branch.objects.create(name=name, info=info)
        return redirect('branches')

class DeleteBranchView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = 'login'
    def test_func(self):
        return self.request.user.is_superuser
    def get(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        return render(request, 'delete-branch.html', {'branch': branch})
    def post(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        branch.delete()
        return redirect('branches')