from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import ExpressionWrapper, F, FloatField
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from .models import *

from django.views import View


class SaleView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        sales = Sale.objects.filter(branch=request.user.branch).order_by('-created_at')
        products = Product.objects.filter(branch=request.user.branch).order_by('name')
        clients = Client.objects.filter(branch=request.user.branch).order_by('name')
        context = {
            'sales': sales,
            'products': products,
            'clients': clients
        }
        return render(request, 'sales.html', context=context)

    def post(self, request):
        product = get_object_or_404(Product, id=request.POST.get('product_id'))
        client = get_object_or_404(Client, id=request.POST.get('client_id'))
        quantity = float(request.POST.get('quantity')) if request.POST.get('quantity') is not None else None
        total_price = float(request.POST.get('total_price')) if request.POST.get('total_price') is not None else None
        paid_price = float(request.POST.get('paid_price')) if request.POST.get('paid_price') is not None else None
        debt_price = float(request.POST.get('debt_price')) if request.POST.get('debt_price') is not None else None

        # check product qunatity
        context = self.check_enough_product(product, quantity)
        if context is not None:
            return render(request, 'warning.html', context=context)

        if debt_price and paid_price:
            total_price = debt_price + paid_price

        if not total_price:
            total_price = product.price * quantity

        if not paid_price and not debt_price:
            paid_price = total_price

        if not debt_price and paid_price:
            debt_price = total_price - paid_price

        if not paid_price and debt_price:
            paid_price = total_price - debt_price

        Sale.objects.create(
            product=product,
            client=client,
            quantity=quantity,
            total_price=total_price,
            paid_price=paid_price,
            debt_price=debt_price,
            user=request.user,
            branch=request.user.branch
        )
        # sub product quantity
        product.quantity -= quantity
        product.save()

        # add client debt
        client.debt += debt_price
        client.save()

        return redirect('sales')

    def check_enough_product(self, product, quantity):
        if product.quantity < quantity:
            warning_message = f"{product.name} so'ralgan miqdor mavjud emas!"
            warning_title = "Maxsulot yetarli emas!"
            back_url = 'sales'
            context = {
                'warning_message': warning_message,
                'warning_title': warning_title,
                'back_url': back_url,
            }
            return context
        return None


class EditSalaView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        sale = get_object_or_404(Sale, branch=request.user.branch, pk=pk)
        products = Product.objects.filter(branch=request.user.branch)
        clients = Client.objects.filter(branch=request.user.branch)

        context = {
            'sale': sale,
            'products': products,
            'clients': clients,
        }
        return render(request, 'edit-sales.html', context=context)

    def post(self, request, pk):
        sale = get_object_or_404(Sale, branch=request.user.branch, pk=pk)

        product = get_object_or_404(Product, id=request.POST.get('product_id'))
        client = get_object_or_404(Client, id=request.POST.get('client_id'))

        quantity = float(request.POST.get('quantity')) if request.POST.get('quantity') else None
        total_price = float(request.POST.get('total_price')) if request.POST.get('total_price') else None
        paid_price = float(request.POST.get('paid_price')) if request.POST.get('paid_price') else None
        debt_price = float(request.POST.get('debt_price')) if request.POST.get('debt_price') else None

        if quantity is None:
            context = {
                'message': 'Miqdor kiritilishi shart!',
                'sale': sale,
                'products': Product.objects.filter(branch=request.user.branch),
                'clients': Client.objects.filter(branch=request.user.branch)
            }
            return render(request, 'warning.html', context=context)

        if debt_price and paid_price:
            total_price = debt_price + paid_price

        if not total_price:
            total_price = product.price * quantity

        if not paid_price and not debt_price:
            paid_price = total_price

        if not debt_price and paid_price:
            debt_price = total_price - paid_price

        if not paid_price and debt_price:
            paid_price = total_price - debt_price

        # AVVALGI MA'LUMOTLARNI SAQLASH
        old_product = sale.product
        old_client = sale.client
        old_quantity = sale.quantity
        old_debt_price = sale.debt_price

        # HECH NARSA O'ZGARMAGAN BO'LSA, BAZAGA TEGMASLIK
        if (product.id == old_product.id and
                client.id == old_client.id and
                quantity == old_quantity and
                total_price == sale.total_price and
                paid_price == sale.paid_price and
                debt_price == old_debt_price):
            # Hech narsa o'zgarmagan - faqat redirect
            return redirect('sales')

        # Qancha mahsulot kerak bo'lishini hisoblash
        if product.id == old_product.id:
            # Bir xil mahsulot - faqat farqni tekshirish kerak
            quantity_difference = quantity - old_quantity
            if quantity_difference > 0:  # Miqdor ko'paygan
                available = old_product.quantity  # Hozirgi mavjud (avvalgisi qaytarilmagan)
                if available < quantity_difference:
                    warning_message = f"{product.name} yetarli emas! Mavjud: {available}, Qo'shimcha kerak: {quantity_difference}"
                    warning_title = "Mahsulot yetarli emas!"
                    back_url = 'sales'
                    context = {
                        'warning_message': warning_message,
                        'warning_title': warning_title,
                        'back_url': back_url,
                    }
                    return render(request, 'warning.html', context=context)
        else:
            # Boshqa mahsulot tanlangan - to'liq miqdorni tekshirish kerak
            if product.quantity < quantity:
                warning_message = f"{product.name} yetarli emas! Mavjud: {product.quantity}, Kerak: {quantity}"
                warning_title = "Mahsulot yetarli emas!"
                back_url = 'sales'
                context = {
                    'warning_message': warning_message,
                    'warning_title': warning_title,
                    'back_url': back_url,
                }
                return render(request, 'warning.html', context=context)

        # AVVALGI MAHSULOT MIQDORINI QAYTARISH (agar mahsulot yoki miqdor o'zgargan bo'lsa)
        if product.id != old_product.id or quantity != old_quantity:
            old_product.quantity += old_quantity
            old_product.save()

        # AVVALGI MIJOZ QARZINI KAMAYTIRISH (agar mijoz yoki qarz o'zgargan bo'lsa)
        if (client.id != old_client.id or debt_price != old_debt_price) and hasattr(old_client, 'debt'):
            old_client.debt -= old_debt_price
            old_client.save()

        # SALE NI YANGILASH
        sale.product = product
        sale.client = client
        sale.quantity = quantity
        sale.total_price = total_price
        sale.paid_price = paid_price
        sale.debt_price = debt_price
        sale.save()

        # YANGI MAHSULOT MIQDORINI KAMAYTIRISH (agar mahsulot yoki miqdor o'zgargan bo'lsa)
        if product.id != old_product.id or quantity != old_quantity:
            product.quantity -= quantity
            product.save()

        # YANGI MIJOZ QARZINI QO'SHISH (agar mijoz yoki qarz o'zgargan bo'lsa)
        if (client.id != old_client.id or debt_price != old_debt_price) and hasattr(client, 'debt'):
            client.debt += debt_price
            client.save()

        return redirect('sales')


class ImportProductView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        import_products = ImportProduct.objects.filter(branch=request.user.branch)
        products = Product.objects.filter(branch=request.user.branch)

        context = {
            'import_products': import_products,
            'products': products,
        }

        return render(request, 'import_products.html', context=context)

    def post(self, request):
        product = get_object_or_404(Product, id=request.POST.get('product_id'))
        quantity = float(request.POST.get('quantity')) if request.POST.get('quantity') is not None else None
        ImportProduct.objects.create(
            product=product,
            buy_price=request.POST.get('buy_price'),
            quantity=quantity,
            user=request.user,
            branch=request.user.branch
        )
        product.quantity += quantity
        product.save()
        return redirect('imports')


class EditImportProductView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        import_product = get_object_or_404(ImportProduct, branch=request.user.branch, pk=pk)
        products = Product.objects.filter(branch=request.user.branch)

        context = {
            'import_product': import_product,
            'products': products,
        }
        return render(request, 'edit-imports.html', context=context)

    def post(self, request, pk):
        importproduct = get_object_or_404(ImportProduct, branch=request.user.branch, pk=pk)
        product = get_object_or_404(Product, branch=request.user.branch, id=request.POST.get("product_id"))

        importproduct.product = product
        importproduct.buy_price = request.POST.get('buy_price')
        importproduct.quantity = request.POST.get('quantity')
        importproduct.save()

        return redirect('imports')


class DeleteImportProductView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        import_product = get_object_or_404(ImportProduct, pk=pk, branch=request.user.branch)
        context = {
            'import_product': import_product,
        }
        return render(request, 'delete-imports.html', context=context)

    def post(self, request, pk):
        import_product = get_object_or_404(ImportProduct, pk=pk, branch=request.user.branch)
        import_product.delete()
        return redirect('imports')


class PaydebtView(LoginRequiredMixin,View):
    login_url = 'login'
    def get(self, request):
        pay_debts = PayDebt.objects.filter(branch=request.user.branch).order_by('-created_at')
        clients = Client.objects.filter(branch=request.user.branch).order_by('-created_at')
        context = {
            'pay_debts': pay_debts,
            'clients': clients,
        }

        return render(request, 'pay-debts.html', context=context)

    def post(self, request):
        client = get_object_or_404(Client, id=request.POST.get('client_id'))
        price = float(request.POST.get('price')) if request.POST.get('price') else None

        if price == 0 or price > client.debt:
            return redirect('pay-debts')

        PayDebt.objects.create(
            client=client,
            price=price,
            description=request.POST.get('description'),
            branch=request.user.branch,
            user=request.user,
        )

        client.debt -= price
        client.save()
        return redirect('pay-debts')

class EditPayDebtView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        pay_debt = get_object_or_404(PayDebt, branch=request.user.branch, pk=pk)
        clients = Client.objects.filter(branch=request.user.branch)

        context = {
            'pay_debt':pay_debt,
            'clients':clients,
        }

        return render(request, 'edit-pay-debts.html', context = context)

    def post(self, request, pk):
        pay_debt = get_object_or_404(PayDebt, branch=request.user.branch, pk=pk)
        client = get_object_or_404(Client, branch=request.user.branch, id=request.POST.get('client_id'))

        pay_debt.price=request.POST.get('price')
        pay_debt.description = request.POST.get('description')
        pay_debt.client = client

        pay_debt.save()

        return redirect('pay-debts')


class DeletePayDebtView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        pay_debt = get_object_or_404(PayDebt, pk=pk, branch=request.user.branch)
        context = {
            'pay_debt': pay_debt,
        }
        return render(request, 'delete-pay-debt.html', context=context)

    def post(self, request, pk):
        pay_debt = get_object_or_404(PayDebt, pk=pk, branch=request.user.branch)
        pay_debt.delete()
        return redirect('pay-debts')
