from django.shortcuts import render, redirect
from django.db.models import Count, Q
from django.views import View
from . models import Feedback, OrderPlaced, Payment, Product, Customer, Cart, Wishlist
from . forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.http import JsonResponse
import razorpay
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import pandas as pd



# Create your views here.

@login_required 
def home(request):
    # totalitem = 0
    # if request.user.is_authenticated:
    #     totalitem=len(Cart.objects.filter(user=request.user))
    return render(request,"app/home.html",locals())

@login_required 
def about(request):
    return render(request,'app/about.html')

@login_required 
def contact(request):
    return render(request,'app/contact.html')

@login_required 
def feedback(request):
    return render(request,'app/Feedback.html')

@login_required 
def ByCategory(request):
    return render(request,'app/ByCategory.html')

@login_required 
def ByMeaning(request):
    return render(request,'app/ByMeaning.html')

@login_required 
def ByColour(request):
    return render(request,'app/ByColour.html')

@login_required 
def ByCrystals(request):
    return render(request,'app/ByCrystals.html')

@login_required 
def Choose(request):
    return render(request,'app/Choose.html')

@login_required 
def Cleanse(request):
    return render(request,'app/Cleanse.html')

@login_required 
def Customize(request):
    return render(request,'app/Customize.html')

@method_decorator(login_required,name='dispatch')
class CategoryView(View):
    def get(self,request,val): 
       product = Product.objects.filter(category=val)
       title = Product.objects.filter(category=val).values('title')
       return render(request,'app/category.html',locals())
    
@method_decorator(login_required,name='dispatch')
class ProductDetail(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        wishlist = Wishlist.objects.filter(Q(product=product) & Q(user=request.user))
        return render(request, 'app/productdetail.html',locals())

   
class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html',locals())
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Congratulations! User Register Successfully")
        else:
            messages.warning(request,"Inavalid Input Data")
        return render(request, 'app/customerregistration.html',locals())

@method_decorator(login_required,name='dispatch')    
class ProfileView(View):
    def get(self,request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html',locals())
    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            village = form.cleaned_data['village']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            pincode = form.cleaned_data['pincode']

            reg = Customer(user=user,name=name,village=village,city=city,mobile=mobile,state=state,pincode=pincode)
            reg.save()
            messages.success(request, "Congratulations! Profile Saved Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request, 'app/profile.html',locals())

@login_required    
def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html',locals())

@method_decorator(login_required,name='dispatch')
class updateAddress(View):
    def get(self,request,pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request, 'app/updateAddress.html',locals())
    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.village = form.cleaned_data['village']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.pincode = form.cleaned_data['pincode']
            add.save()
            messages.success(request,"Congratulations! Profile Updated Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return redirect("address")
    
@login_required 
def add_to_cart(request):
    user=request.user
    product_id=request.GET.get("prod_id")
    product = Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    return redirect("/cart")
    

@login_required
def show_cart(request):
    user = request.user
    cart= Cart.objects.filter(user=user)
    amount=0
    for p in cart:
        value = p.quantity * p.product.discounted_price
        amount= amount+value
    totalamount = amount + 40
    return render(request, 'app/addtocart.html',locals())

def show_wishlist(request):
    user = request.user
    product= Wishlist.objects.filter(user=user)
    return render(request, 'app/wishlist.html',locals())

@method_decorator(login_required,name='dispatch')
class checkout(View):
    def get(self,request):
        user=request.user
        add=Customer.objects.filter(user=user)
        cart_items=Cart.objects.filter(user=user)
        famount = 0
        for p in cart_items:
            value=p.quantity * p.product.discounted_price
            famount = famount + value
        totalamount = famount + 40
        razoramount = int(totalamount * 100)
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        data = {"amount" :razoramount, "currency":"INR","receipt":"order_rcptid_12"}
        payment_response = client.order.create(data=data)
        print(payment_response)
#         {'id': 'order_MfrhWc9zmEgv6L', 'entity': 'order', 'amount': 32900, 'amount_paid': 0, 'amount_due': 32900, 'currency': 'INR', 'receipt': 'order_rcptid_12', 'offer_id': None, 'status': 'created', 'attempts': 0, 'notes': [], 'created_at': 1695491366}
        order_id = payment_response['id']
        order_status = payment_response['status']
        if order_status == 'created':
            payment = Payment(
                user=user,
                amount=totalamount,
                razorpay_order_id = order_id,
                razorpay_payment_status = order_status
            )
            payment.save()
        return render(request, 'app/checkout.html',locals())

@login_required
def payment_done(request):
    order_id = request.GET.get('order_id')
    payment_id =  request.GET.get('payment_id')
    cust_id = request.GET.get('cust_id')
    #print("payment_done :oid=",order_id,"pid=",payment_id,"cid=",cust_id)
    user=request.user
    #return redirect("orders")
    customer = Customer.objects.get(id=cust_id)
    #To update payment status and payment payment id
    payment = Payment.objects.get(razorpay_order_id=order_id)
    payment.paid=True
    payment.razorpay_payment_id = payment_id
    payment.save()
    #To save order details
    cart=Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity,payment=payment).save()
        c.delete()
    return redirect("orders")

@login_required
def orders(request):
    order_placed=OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html',locals())

@login_required
def plus_cart(request):
    if request.method == 'GET' :
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
#         print(prod_id)
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)

@login_required 
def minus_cart(request):
    if request.method == 'GET' :
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity-=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        #print(prod_id)
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)

@login_required     
def remove_cart(request):
    if request.method == 'GET' :
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        #print(prod_id)
        data={
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)
 
def plus_wishlist(request):
    if request.method =='GET':
        prod_id = request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user
        Wishlist(user=user, product=product).save()
        data={
            'message':'Item Sucessfully Added to Wishlist',
        }
        return JsonResponse(data)

 
def minus_wishlist(request):
    if request.method =='GET':
        prod_id = request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user
        Wishlist.objects.filter(user=user, product=product).delete()
        data={
            'message':'Item Successfully Removed from Wishlist',
        }
        return JsonResponse(data)
    
@login_required    
def search(request):
    query = request.GET['search']
    product = Product.objects.filter(Q(title__icontains = query))
    return render(request,"app/search.html",locals())

@login_required 
def feedback(request):
    if request.method=="POST":
        feedback=Feedback()
        name=request.POST.get('name')
        email=request.POST.get('email')
        comment=request.POST.get('comment')
        feedback.name=name
        feedback.email=email
        feedback.comment=comment
        feedback.save()
        # return HttpResponse("<center><h1>THANKS FOR YOUR FEEDBACK</h1><center>")
        return redirect("/")
    return render(request, 'app/feedback.html',locals())