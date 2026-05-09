import json

from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from . models import Product, Category, Customer,Orders,ShoppingCart,Owner,DeliveryPerson,MoneyCollection,Product2, HealthCondition, Review, Wishlist
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from django.db.models import Avg, Count, Sum


def index(request):
    obj = Product.objects.all()
    return render(request,'index.html', {'fruits':obj})


def ownerdashboard(request):
    total_orders = Orders.objects.count()
    total_customers = Customer.objects.count()
    total_products = Product.objects.count()
    total_sales = Orders.objects.aggregate(Sum('price'))['price__sum'] or 0
    recent_orders = Orders.objects.order_by('-order_date')[:10]
    low_stock_products = Product.objects.filter(stock__lte=5)

    context = {
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_products': total_products,
        'total_sales': total_sales,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
    }
    return render(request,'ownerdashboard.html', context)

def about(request):
    return render(request,'about.html')

def vieworders(request):
    orders = Orders.objects.all()
    return render(request,'vieworders.html',{'orders':orders})


def productPage(request):
    if request.method == "POST":
        return redirect('product')
    else:
        category_id=request.GET.get('category')
        data = {}
        if category_id:
           products= Product.get_products_by_categoryid(category_id)
        else:
          products = Product.get_all_products()
        category = Category.get_all_category()

        # Add reviews and average rating for each product
        for product in products:
            reviews = Review.objects.filter(product=product)
            product.avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
            product.review_count = reviews.count()
            product.reviews = reviews[:5]  # Show latest 5 reviews

        # Set flags for showing stock status (only for in-stock products)
        for product in products:
            if product.stock > 0:
                product.show_stock = True
            else:
                product.show_stock = False
                # Special case: show out of stock for Moong Whole
                if product.name == "Moong Whole":
                    product.show_out_of_stock = True

        data['products'] = products
        data['category'] = category
        return render(request, 'product.html', data)


def register(request):
    if request.method == 'POST':
        err=None
        name= request.POST.get('name')
        email = request.POST.get('email')
        passwd = request.POST.get('password')
        addr = request.POST.get('address')
        pin = request.POST.get('pincode')
        phone = request.POST.get('phone')
        gen = request.POST.get('gender')

        #Validation
        values={'name':name,
                'email':email,
                'addr':addr,
                'pin':pin,
                'phone':phone,
                'gen':gen,}
        customer = Customer(name=name, gender=gen, address=addr, pincode=pin, contactno=phone, emailaddress=email,
                            password=passwd)

        if not name.isalpha():
            err="Invalid Name, please try again"
        if not phone.isnumeric() or len(phone)<10:
            err="Invalid Contact Number, please try again"
        if not pin.isnumeric():
            err="Invalid Pincode, please try again"
        if customer.is_exists():
            err="Email Already Exists"
        data={}
        data['err']=err
        data['values']=values
        if err:
            return render(request, 'register.html',data)
        #customer.password=make_password(passwd)
        customer.save()
        myuser = User.objects.create_user(username=email,email=email, password=passwd)
        myuser.save()

        err = "You are registered! Try Logging in"
        return render(request, 'login.html',{'err':err})
    else:
        return render(request, 'register.html')
    

def ownersignin(request):
    if request.method == 'POST':
        email1 = request.POST.get('email')
        password1 = request.POST.get('password')
        try:
            user=Owner.objects.get(email=email1,password=password1)
            request.session['email']=user.email
            return redirect('ownerdashboard')
        except Owner.DoesNotExist:
            return render(request,'ownerlogin.html')
        
    return render(request,'ownerlogin.html')


def search_results(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if category_id:
        products = products.filter(category_id=category_id)

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    categories = Category.get_all_category()

    # Add reviews and average rating for each product
    for product in products:
        reviews = Review.objects.filter(product=product)
        product.avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        product.review_count = reviews.count()

    return render(request, 'search_results.html', {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'min_price': min_price,
        'max_price': max_price
    })



@login_required(redirect_field_name='login')
def suggestion_view(request):
    health_conditions = HealthCondition.objects.all()
    products = None

    # Mapping of health conditions to specific product keywords (based on actual products)
    health_product_mapping = {
        'diabetes management': ['moong', 'psyllium', 'moringa', 'tulsi green tea', 'amalaki'],
        'heart health': ['coconut oil', 'mustard oil', 'sunflower oil', 'organic cow ghee', 'tulsi ginger turmeric'],
        'digestive health': ['tulsi green tea', 'psyllium', 'amalaki', 'ginger', 'turmeric'],
        'immune support': ['tulsi ginger turmeric', 'assam black tea', 'moringa', 'amalaki', 'turmeric formula'],
        'energy & vitality': ['tulsi green tea classic', 'moringa', 'brown chana', 'bengal gram', 'urad whole'],
        'weight management': ['moong', 'psyllium', 'tulsi green tea', 'moringa', 'amalaki'],
        'joint health': ['turmeric', 'ginger', 'tulsi ginger turmeric', 'moringa', 'amalaki'],
        'skin health': ['turmeric', 'tulsi green tea', 'moringa', 'amalaki', 'coconut oil'],
        'liver health': ['turmeric', 'tulsi ginger turmeric', 'moringa', 'amalaki', 'ginger'],
        'bone health': ['moringa', 'sesame seeds', 'brown chana', 'bengal gram', 'urad whole'],
    }

    if request.method == 'POST':
        health_condition_id = request.POST.get('health_condition')
        if health_condition_id:
            try:
                health_condition = HealthCondition.objects.get(id=health_condition_id)
                condition_name = health_condition.name.lower()
                
                # Get keywords for this condition
                keywords = health_product_mapping.get(condition_name, [])
                
                # Search for products matching these keywords in the actual Product model
                from django.db.models import Q
                query = Q()
                for keyword in keywords:
                    # Prioritize exact name matches first
                    query |= Q(name__iexact=keyword)
                    # Then partial name matches
                    query |= Q(name__icontains=keyword)
                    # Then description matches
                    query |= Q(desc__icontains=keyword)
                
                products = Product.objects.filter(query).distinct()[:8]  # Limit to 8 products
                
                # If no products found with keywords, provide some general healthy options
                if not products:
                    general_healthy = ['tulsi', 'tea', 'organic', 'whole']
                    general_query = Q()
                    for term in general_healthy:
                        general_query |= Q(name__icontains=term) | Q(desc__icontains=term)
                    products = Product.objects.filter(general_query).distinct()[:4]
            except HealthCondition.DoesNotExist:
                products = None

    # Get product data for the chatbot
    all_products = Product.objects.all()
    product_data = []
    for product in all_products:
        product_data.append({
            'name': product.name,
            'desc': product.desc,
            'category': product.category.name if product.category else 'General',
            'price': float(product.price),
            'organic': f"{product.name} is sourced and handled with organic-quality care in this project, focusing on natural and low-chemical methods.",
            'delivery': 'Delivery is typically available within 3-5 business days for this item.',
            'quantity_help': 'Quantity can be selected during checkout. Each item is sold per unit, and you can order multiple units as desired.',
        })

    context = {
        'health_conditions': health_conditions,
        'products': products,
        'product_data_json': json.dumps(product_data),
        'active_tab': 'assistant' if request.method == 'POST' and not products else 'guide'
    }
    return render(request, 'suggestion.html', context)


def chatbot_view(request):
    products = Product.objects.all()
    product_data = []
    for product in products:
        product_data.append({
            'name': product.name,
            'desc': product.desc,
            'category': product.category.name if product.category else 'General',
            'price': float(product.price),
            'organic': f"{product.name} is sourced and handled with organic-quality care in this project, focusing on natural and low-chemical methods.",
            'delivery': 'Delivery is typically available within 3-5 business days for this item.',
            'quantity_help': 'Quantity can be selected during checkout. Each item is sold per unit, and you can order multiple units as desired.',
        })

    return render(request, 'chatbot.html', {
        'product_data_json': json.dumps(product_data)
    })


def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        myuser = authenticate(username=email, password=password)
        if myuser is not None:
            login(request, myuser)
            try:
                cart=ShoppingCart.objects.filter(customer=Customer.objects.get(emailaddress=request.user.username))
            except Exception as e:
                print(e)
                cart=[]
            request.session['cart']=len(cart)
            return redirect('user')
        else:
            msg="Incorrect Id or password"
            return render(request,'login.html',{'msg':msg})
    return render(request,'login.html')






@login_required(redirect_field_name='login')
def user(request):
    customer = Customer.get_customer_by_email(request.user.username)
    # Generate a dynamic welcome message based on hour of the day
    from datetime import datetime
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning! Start your healthy journey today."
    elif hour < 18:
        greeting = "Good afternoon! Explore our wellness products."
    else:
        greeting = "Good evening! Take care of your health with our organic products."
    
    data={}
    if request.method=='POST':
        msg=None
        err=None
        current_password=request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if customer.password==current_password:
            if new_password==confirm_password:
                customer.password=new_password
                customer.save()
                myuser=User.objects.get(username=request.user.username)
                myuser.password=make_password(new_password)
                myuser.save()
                data['msg']='Password Changed Successfully'

            else:
                return render(request, 'changepass.html', {'err': 'New password and confirm password does not match'})
        else:
            return render(request,'changepass.html',{'err':'Incorrect Password'})
    data['customer']=customer
    data['welcome_message'] = greeting
    return render(request,'user.html',data)

@login_required(redirect_field_name='login')
def orders(request):
    orders=Orders.objects.filter(customer=request.user.username).order_by('-order_date')
    return render(request,'orders.html',{'orders':orders})

@login_required(redirect_field_name='login')
def changepass(request):
    return render(request,'changepass.html')

def signout(request):
    logout(request)
    request.session.flush()
    return redirect('index')


@login_required(redirect_field_name='login')
def buynow(request):
    data={}
    if request.method=='GET':
        total=request.GET.get('total')
        if int(total) < 1:
            err="Total cannot be zero"
            return redirect('/mycart/?err='+err)
        method = "add_to_cart"
        customer = Customer.get_customer_by_email(request.user.username)
        cart=ShoppingCart.objects.filter(customer=customer)
        data['cart']=cart

    else:
        method = "buy_now"
        productid=request.POST.get('product')
        #print(productid)
        product=Product.get_product_by_id(productid)
        email=request.user.username
        customer=Customer.get_customer_by_email(email)
        data['product']=product
        data['customer']=customer
    data['method']=method
    return render(request,'confirm.html',data)

@login_required(redirect_field_name='login')
def checkout(request):
    if request.method=='GET':
        customer = Customer.get_customer_by_email(request.user.username)
        cart = ShoppingCart.objects.filter(customer=customer)
        for items in cart:
            order = Orders(customer=items.customer, product=items.product, quantity=items.quantity,
                           price=items.product.price, address=items.customer.address, pincode=items.customer.pincode)
            order.save()
        ShoppingCart.objects.filter(customer=Customer.get_customer_by_email(request.user.username)).delete()
        request.session['cart'] = 0

    else:
        product=Product.get_product_by_id(request.POST.get('productid'))
        customer =Customer.get_customer_by_email(request.POST.get('email'))
        quantity = request.POST.get('quantity')
        order=Orders(customer=customer,product=product,price=product.price,address=customer.address,pincode=customer.pincode,quantity=quantity)
        order.save()

    return render(request,'checkout.html')


@login_required(redirect_field_name='login')
def mycart(request):
    if request.method == "GET" and request.GET.get('flag') == "add_to_cart":
        category = request.GET.get('category', '')
        try:
            product = Product.objects.get(id=request.GET.get('product_id'))
            customer = Customer.get_customer_by_email(request.user.username)

            if product.stock <= 0:
                msg = "❌ This product is currently out of stock"
                return redirect('/product/?msg=' + msg + '&category=' + category)

            # Check if product is already in cart
            existing_cart = ShoppingCart.objects.filter(customer=customer, product=product).first()
            if existing_cart:
                existing_cart.quantity += 1
                existing_cart.save()
                msg = f"✅ {product.name} quantity updated in cart!"
            else:
                cart = ShoppingCart(customer=customer, product=product, quantity=1)
                cart.save()
                msg = f"✅ {product.name} added to cart successfully!"
            
            # Update session cart count
            request.session['cart'] = request.session.get('cart', 0) + 1
            return redirect('/product/?msg=' + msg + '&category=' + category)
        except Product.DoesNotExist:
            msg = "❌ Product not found"
            return redirect('/product/?msg=' + msg + '&category=' + category)
        except Exception as e:
            msg = "❌ Error adding product to cart"
            return redirect('/product/?msg=' + msg + '&category=' + category)
    
    try:
        customer = Customer.objects.get(emailaddress=request.user.username)
        cart = ShoppingCart.objects.filter(customer=customer)
        total = sum([cartitem.product.price * cartitem.quantity for cartitem in cart])
    except:
        cart = []
        total = 0
    
    return render(request, 'mycart.html', {'cart': cart, 'total': total})

@login_required(redirect_field_name='login')
def update_cart(request):
    err=None
    if request.method=='POST':
        cart_item_id=request.POST.get('cart_item_id')
        quantity=request.POST.get('quantity')
        try:
            if int(quantity) > 0:
                cart=ShoppingCart.objects.get(id=cart_item_id)
                cart.quantity=quantity
                cart.save()
                msg = "✅ Cart updated successfully!"
                return redirect('/mycart/?msg=' + msg)
            else:
                err="❌ Quantity cannot be less than 1"
        except:
            err="❌ Error updating cart"
    elif request.method=='GET' and request.GET.get('cart_item'):
        cart_item_id=request.GET.get('cart_item')
        try:
            ShoppingCart.objects.get(id=cart_item_id).delete()
            request.session['cart'] = max(0, request.session.get('cart', 1) - 1)
            msg = "✅ Product removed from cart"
            return redirect('/mycart/?msg=' + msg)
        except Exception as e:
            err="❌ Error removing product"
    else:
        try:
            customer = Customer.get_customer_by_email(request.user.username)
            ShoppingCart.objects.filter(customer=customer).delete()
            request.session['cart'] = 0
            err="✅ Cart cleared successfully"
        except Exception as e:
            err="❌ Error clearing cart"
    if err:
        return redirect('/mycart/?msg='+err)
    else:
        return redirect('/mycart/')
    



def add_delivery_person(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        city = request.POST.get('city')
        collected_money = request.POST.get('collected_money')
        availability = request.POST.get('availability')

        # Create new DeliveryPerson instance
        delivery_person = DeliveryPerson(
            first_name=first_name,
            phone_number=phone_number,
            email=email,
            city=city,
            collected_money=0,
            availability=1
        )
        delivery_person.save()

        return redirect('index')  # Assuming you have a 'home' named view to redirect to

    return render(request, 'add_delivery_person.html')



def delivery_persons(request):
    delivery_persons = DeliveryPerson.objects.all()
    return render(request, 'delivery_persons.html', {'delivery_persons': delivery_persons})



def transfer_money(request):
    delivery_persons = DeliveryPerson.objects.all()
    if request.method == 'POST':
        delivery_person_id = request.POST.get('email')
        try:
            delivery_person = DeliveryPerson.objects.get(email=delivery_person_id)
            money_collected = delivery_person.collected_money
            # Create MoneyCollection object
            money_collection = MoneyCollection(date=timezone.now(), money_collected=money_collected)
            money_collection.save()
            # Reset collected money for the delivery person
            delivery_person.collected_money = 0
            delivery_person.save()
            messages.success(request, f"The money collected from {delivery_person.first_name} has been transferred successfully.")
        except DeliveryPerson.DoesNotExist:
            messages.error(request, "Delivery person does not exist.")
        return redirect('transfer_money')
    return render(request, 'transfer_money.html', {'delivery_persons': delivery_persons})




def deliveryboylogin(request):
    if request.method == 'POST':
        email1 = request.POST.get('email')
        password1 = request.POST.get('password')
        try:
            user=DeliveryPerson.objects.get(email=email1,password=password1)
            request.session['email']=user.email
            request.session['deliveryboycity']=user.city
            return redirect('deliveryboydsb')
        except Owner.DoesNotExist:
            return render(request,'deliveryboylogin.html')
        
    return render(request,'deliveryboylogin.html')


def deliveryboy_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'email' not in request.session:
            return redirect('deliveryboylogin')  # Redirect to login if email is not in session
        return view_func(request, *args, **kwargs)
    return wrapper


def deliveryboydsb(request):
    if request.method == 'POST':
        productname = request.POST.get('productname')
        productprice = Decimal(request.POST.get('productprice'))
        customeremail = request.POST.get('customeremail')

        # Delete the order
        Orders.objects.filter(product__name=productname).delete()

        # Retrieve the delivery person associated with the current session
        delivery_person = DeliveryPerson.objects.get(email=request.session['email'])

        # Update collected money
        delivery_person.collected_money += productprice
        delivery_person.save()

        # Redirect to prevent resubmission of form data
        return redirect('deliveryboydsb')

    delivery_person_city = request.session.get('deliveryboycity')
    orders = Orders.objects.filter(address=delivery_person_city)

    return render(request, 'deliveryboydsb.html', {'orders': orders})


@login_required
def add_to_wishlist(request, product_id):
    product = Product.objects.get(id=product_id)
    customer = Customer.get_customer_by_email(request.user.username)
    wishlist_item, created = Wishlist.objects.get_or_create(customer=customer, product=product)
    if created:
        messages.success(request, f"{product.name} added to wishlist!")
    else:
        messages.info(request, f"{product.name} is already in your wishlist.")
    return redirect('product')


@login_required
def remove_from_wishlist(request, product_id):
    product = Product.objects.get(id=product_id)
    customer = Customer.get_customer_by_email(request.user.username)
    Wishlist.objects.filter(customer=customer, product=product).delete()
    messages.success(request, f"{product.name} removed from wishlist.")
    return redirect('wishlist')


@login_required
def wishlist(request):
    customer = Customer.get_customer_by_email(request.user.username)
    wishlist_items = Wishlist.objects.filter(customer=customer).select_related('product')
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})


@login_required
def add_review(request, product_id):
    if request.method == 'POST':
        product = Product.objects.get(id=product_id)
        customer = Customer.get_customer_by_email(request.user.username)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        Review.objects.create(customer=customer, product=product, rating=rating, comment=comment)
        messages.success(request, "Review added successfully!")
        return redirect('product')
    return redirect('product')