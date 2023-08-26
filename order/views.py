import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import CartItem, Product, Order, OrderItem
from django.conf import settings


def home(request):
    products = Product.objects.all()
    cart_items = get_cart_items(request)
    cart_total_items = sum(item.quantity for item in cart_items)
    cart_total_price = sum(item.product.price * item.quantity for item in cart_items)
    latest_order = Order.objects.latest('order_time')
    order_status = latest_order.order_status if latest_order else None

    context = {
        'products': products,
        'cart_items': cart_items,
        'cart_total_items': cart_total_items,
        'cart_total_price': cart_total_price,
    }

    context = {
        'cart_items': cart_items,
        'products': products,
        'order_status': order_status,
    }

    return render(request, 'home.html', context)


def get_cart_items(request):
    cart_items = []
    if 'cart' in request.session:
        cart = request.session['cart']
        product_ids = cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            cart_item = CartItem(product=product, quantity=cart[str(product.id)])
            cart_items.append(cart_item)
    return cart_items


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    try:
        cart_item = cart[str(product_id)]
        cart[product_id] += 1
    except KeyError:
        cart[str(product_id)] = 1
    except Exception as e:
        messages.error(request, 'An error occurred while adding the product to the cart.')
        return redirect('home')

    request.session['cart'] = cart
    messages.success(request, 'Product added to cart successfully.')
    return redirect('home')


def increase_quantity(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            cart[str(product_id)] += 1
            request.session['cart'] = cart
    return redirect('home')


def decrease_quantity(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            if cart[str(product_id)] > 1:
                cart[str(product_id)] -= 1
            else:
                del cart[str(product_id)]
            request.session['cart'] = cart
    return redirect('home')


from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt


# Other imports...

@csrf_exempt
def process_checkout(request):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        name = request.POST.get('name')
        mobile_number = request.POST.get('mobile_number')
        address = request.POST.get('address')

        # Example logic to handle different payment methods
        if payment_method == 'cash_on_delivery':
            # Handle cash on delivery logic
            pass
        elif payment_method == 'upi':
            # Handle UPI logic
            return redirect('qr_code')  # Redirect to QR code page

        # Example logic to handle the address
        if address == 'home':
            # Handle home address logic
            pass
        elif address == 'office':
            # Handle office address logic
            pass

        # You can store the necessary information in the Order model or any other relevant model

        # Clear the cart
        request.session.pop('cart', None)

        return redirect('order_success')

    return render(request, 'process_checkout.html')


def order_success(request):
    return render(request, 'order_success.html')


from django.contrib import messages


def change_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('order_status')
        order.order_status = new_status
        order.save()
        messages.success(request, 'Order status updated successfully.')
        return redirect('order_detail', order_id=order.id)

    context = {
        'order': order
    }
    return render(request, 'change_order_status.html', context)


def product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'product.html', {'product': product})


def checkout(request):
    cart = request.session.get('cart', {})
    cart_items = []
    cart_total = Decimal('0.00')
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        total = product.price * quantity
        cart_item = {
            'product': product,
            'quantity': quantity,
            'total': total
        }
        cart_items.append(cart_item)
        cart_total += total

    cart_total = cart_total.quantize(Decimal('0.00'))

    context = {
        'cart_items': cart_items,
        'cart_total': cart_total
    }

    return render(request, 'checkout.html', context)


# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from .models import Product, Order
from .forms import QRCodeForm
import razorpay
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from decimal import Decimal
from .models import Product, Order, QRCode

# Replace these with your actual Razorpay credentials

RAZORPAY_KEY_ID = 'rzp_test_J4nh1r5VKhWq8K'
RAZORPAY_KEY_SECRET = 'eJSUdYl3mrNLFJ1zYuenv9mh'


@csrf_exempt
def place_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')

    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        mobile_number = request.POST.get('mobile_number')
        payment_method = request.POST.get('payment_method')
        address_type = request.POST.get('address')

        if payment_method == 'cod':
            # Handle cash on delivery logic here
            # For COD, you may want to update the order_status to 'prepared' or 'delivered' as per your workflow

            for product_id, quantity in cart.items():
                product = get_object_or_404(Product, pk=product_id)
                order = Order(
                    user_name=user_name,
                    mobile_number=mobile_number,
                    product=product,
                    quantity=quantity,
                    payment_method=payment_method,
                    order_status='pending',  # Update the order_status for COD
                    address_type=address_type,
                    order_time=timezone.now(),
                )
                order.save()

            del request.session['cart']
            messages.success(request, 'Order placed successfully (Cash on Delivery).')
            return redirect('order_success')

        elif payment_method == 'other':

            for product_id, quantity in cart.items():
                product = get_object_or_404(Product, pk=product_id)
                order = Order(
                    user_name=user_name,
                    mobile_number=mobile_number,
                    product=product,
                    quantity=quantity,
                    payment_method=payment_method,
                    order_status='pending',  # You might want to set a different initial status
                    address_type=address_type,
                    order_time=timezone.now(),
                )
                order.save()
            del request.session['cart']

            # Assuming you have a separate view named 'qr_code', where users can make other payments
            return redirect('qr_code')  # You need to define this view in your Django application

            # Handle other payment methods logic here
            # Redirect the user to the respective payment page or process the payment as required

            # Example: If you have a separate view named 'other_payment', you can redirect to it
            # return redirect('qr_code')

        elif payment_method == 'upi':
            for product_id, quantity in cart.items():
                product = get_object_or_404(Product, pk=product_id)
                order = Order(
                    user_name=user_name,
                    mobile_number=mobile_number,
                    product=product,
                    quantity=quantity,
                    payment_method=payment_method,
                    order_status='pending',  # You can set an appropriate initial status
                    address_type=address_type,
                    order_time=timezone.now(),
                )
                order.save()

            del request.session['cart']
            messages.success(request, 'Order placed successfully (UPI).')
            return redirect('order_success')  # Redirect to the order success page


        else:
            messages.error(request, 'Invalid payment method selected.')
            return redirect('checkout')

    cart_items = []
    cart_total = Decimal('0.00')
    cart_quantity = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        total = product.price * quantity
        cart_item = {
            'product': product,
            'quantity': quantity,
            'total': total
        }
        cart_items.append(cart_item)
        cart_total += total
        cart_quantity += quantity

    cart_total = cart_total.quantize(Decimal('0.00'))

    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'cart_quantity': cart_quantity,
    }

    return render(request, 'checkout.html', context)


from django.shortcuts import redirect


def clear_session(request):
    try:
        del request.session['cart']
        return redirect('home')  # Redirect to the home page or any other desired page
    except KeyError:
        return redirect('home')  # Redirect to the home page or any other desired page


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt


# Other views...

def cart(request):
    cart_items = get_cart_items(request)
    return render(request, 'cart.html', {'cart_items': cart_items})


# Other views...

def remove_from_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            del cart[str(product_id)]
            request.session['cart'] = cart
            messages.success(request, 'Product removed from cart successfully.')
    return redirect('cart')


# Other views...


"""
import qrcode

def qr_code(request):
    # Generate the QR code
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data('https://example.com')  # Replace 'https://example.com' with your actual QR code data
    qr.make(fit=True)

    # Create an image from the QR code data
    qr_image = qr.make_image(fill_color="black", back_color="white")

    # Prepare the image for rendering in the template
    qr_image_base64 = qr_image.get_image().tobytes()
    qr_image_data = base64.b64encode(qr_image_base64).decode('utf-8')

    context = {
        'qr_image_data': qr_image_data
    }
    return render(request, 'qr_code.html', context)
    
    """

from django.shortcuts import render
from .models import QRCode


def qr_code(request):
    qr_code_obj = QRCode.objects.last()  # Assuming there is only one QR code entry, change as needed
    if qr_code_obj:
        context = {
            'qr_image_url': qr_code_obj.image.url
        }
        return render(request, 'qr_code.html', context)

    return HttpResponse("No QR code available.")


"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Order, Product
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
from django.utils import timezone


def get_order_status(payment_method):
    if payment_method == 'cod':
        return 'Ordered'
    elif payment_method == 'qr_code':
        return 'Prepared'
    elif payment_method == 'delivered':
        return 'Delivered'
    else:
        return 'Pending'
        
        """

# Import required modules and models

# Other views...
"""
@csrf_exempt
def process_payment(request):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        if payment_method == 'rozer_pay':
            # Handle Rozer Pay payment logic
            return redirect('rozer_pay_payment')  # Replace 'rozer_pay_payment' with the URL name for Rozer Pay payment view

        elif payment_method == 'paytm':
            # Handle Paytm payment logic
            return redirect('paytm_payment')  # Replace 'paytm_payment' with the URL name for Paytm payment view

    # Redirect back to the checkout page if the payment method is not selected or invalid
    return redirect('checkout')

def rozer_pay_payment(request):
    # Handle Rozer Pay payment process and render the payment.html template with Rozer Pay details
    # Add your Rozer Pay payment gateway logic here
    return render(request, 'payment.html', {'payment_method': 'Rozer Pay'})

def paytm_payment(request):
    # Handle Paytm payment process and render the payment.html template with Paytm details
    # Add your Paytm payment gateway logic here
    return render(request, 'payment.html', {'payment_method': 'Paytm'})

# Other views...

# views.py
"""
from django.shortcuts import render, redirect
from .models import Order
from django.views.decorators.csrf import csrf_exempt
import razorpay
from .constants import PaymentStatus
import json


def order_payment(request):
    if request.method == "POST":
        name = request.POST.get("name")
        amount = request.POST.get("amount")
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create(
            {"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"}
        )
        order = Order.objects.create(
            name=name, amount=amount, provider_order_id=razorpay_order["id"]
        )
        order.save()
        return render(
            request,
            "payment.html",
            {
                "callback_url": "http://" + request.get_host() + "/razorpay/callback/",
                "razorpay_key": RAZORPAY_KEY_ID,
                "order": order,
            },
        )
    return render(request, "payment.html")


@csrf_exempt
def callback(request):
    def verify_signature(response_data):
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        return client.utility.verify_payment_signature(response_data)

    if "razorpay_signature" in request.POST:
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.signature_id = signature_id
        order.save()
        if not verify_signature(request.POST):
            order.status = PaymentStatus.SUCCESS
            order.save()
            return render(request, "callback.html", context={"status": order.status})
        else:
            order.status = PaymentStatus.FAILURE
            order.save()
            return render(request, "callback.html", context={"status": order.status})
    else:
        payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
        provider_order_id = json.loads(request.POST.get("error[metadata]")).get(
            "order_id"
        )
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.status = PaymentStatus.FAILURE
        order.save()
        return render(request, "callback.html", context={"status": order.status})


def payment_success(request):
    # Add any logic or data you want to display on the payment success page
    return render(request, 'payment_success.html')


from django.shortcuts import render, redirect


def other_payment(request):
    # You can fetch any necessary data here to display on the payment page
    qr_code_image_url = 'path_to_qr_code_image.png'
    upi_id = 'your_upi_id@example.com'  # Replace with your actual UPI ID

    context = {
        'qr_code_image_url': qr_code_image_url,
        'upi_id': upi_id,
    }

    try:
        # Simulate a successful payment by raising an exception
        # In a real scenario, you would perform the actual payment processing here
        # and catch the appropriate exception if the payment is not successful.
        # For demonstration purposes, we are raising an exception to simulate a successful payment.
        raise Exception("Payment successful")

        # If the payment is successful, redirect to the payment success page
        return redirect('order_success')  # You need to define this view in your Django application

    except:
        # If the payment is not successful, handle the exception here (e.g., show an error message)
        error_message = "Payment was not successful. Please try again."
        context['error_message'] = error_message

    return render(request, 'other_payment.html', context)


def about_us(request):
    return render(request, 'about_us.html')


from django.shortcuts import render, redirect

def process_upi_payment(request):
    if request.method == 'GET':
        upi_id = request.GET.get('upi_id')

        if upi_id:
            # Implement your UPI payment logic here
            # You can use the upi_id to process the payment
            # If the payment is successful, you can redirect to the success page
            return redirect('payment_success')  # Replace with your success page URL
        else:
            # UPI ID not provided, handle accordingly
            return redirect('qr_code')  # Redirect back to the QR code page or an error page

    return redirect('qr_code')  # Redirect back to the QR code page if the method is not GET
