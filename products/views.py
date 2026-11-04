from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Product, Order, OrderItem
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Product


def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'products/product_list.html', {
        'products': products
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products/product_detail.html', {
        'product': product
    })


def add_to_cart(request, product_id):
    if request.method != 'POST':
        return redirect('product_detail', product_id=product_id)

    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    key = str(product.id)
    quantity = int(cart.get(key, 0))

    if product.stock > quantity:
        cart[key] = quantity + 1

    request.session['cart'] = cart
    return redirect('cart')


def view_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for product_id, quantity in cart.items():
        product = Product.objects.filter(id=product_id).first()

        if product is None or product.stock <= 0:
            continue

        quantity = min(int(quantity), product.stock)
        subtotal = product.price * quantity
        total += subtotal

        items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    return render(request, 'products/cart.html', {
        'items': items,
        'total': total,
    })


@require_POST
def update_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    key = str(product.id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    if quantity <= 0:
        cart.pop(key, None)
    elif quantity <= product.stock:
        cart[key] = quantity

    request.session['cart'] = cart
    return redirect('cart')


@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    return redirect('cart')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('account')
    else:
        form = UserCreationForm()

    return render(request, 'products/register.html', {
        'form': form
    })


@login_required
def account(request):
    return render(request, 'products/account.html')


@require_POST
def logout_view(request):
    logout(request)
    return redirect('product_list')

@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('shipping_address', '').strip()

        if not full_name or not phone or not address:
            return render(request, 'products/checkout.html', {
                'error': 'Please complete all shipping fields.'
            })

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    full_name=full_name,
                    phone=phone,
                    shipping_address=address,
                    total_amount=Decimal('0.00')
                )

                total = Decimal('0.00')

                for product_id, quantity in cart.items():
                    try:
                        quantity = int(quantity)
                        product = Product.objects.get(
                            id=int(product_id)
                        )
                    except (ValueError, TypeError, Product.DoesNotExist):
                        raise ValueError(
                            'A product in your cart is invalid.'
                        )

                    if quantity <= 0 or product.stock < quantity:
                        raise ValueError(
                            f'Insufficient stock for {product.name}. '
                            'Please update your cart.'
                        )

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        quantity=quantity,
                        unit_price=product.price
                    )

                    product.stock -= quantity
                    product.save(update_fields=['stock'])

                    total += product.price * quantity

                order.total_amount = total
                order.save(update_fields=['total_amount'])

        except ValueError as exc:
            return render(request, 'products/checkout.html', {
                'error': str(exc)
            })

        request.session['cart'] = {}
        return redirect('order_success', order_id=order.id)

    items = []
    total = Decimal('0.00')

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            quantity = int(quantity)
        except (ValueError, TypeError, Product.DoesNotExist):
            continue

        if quantity <= 0 or product.stock < quantity:
            continue

        subtotal = product.price * quantity
        items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })
        total += subtotal

    if not items:
        return redirect('cart')

    return render(request, 'products/checkout.html', {
        'items': items,
        'total': total,
    })


@login_required
def order_success(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )
    return render(request, 'products/order_success.html', {
        'order': order
    })


@login_required
def order_history(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'products/order_history.html', {
        'orders': orders
    })
