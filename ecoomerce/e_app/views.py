from django.shortcuts import render
from e_app.models import Product
from math import ceil
import razorpay
from django.conf import settings
from .models import  Orders
from .models import  OrderUpdate
from django.shortcuts import redirect
from django.contrib import messages

def home(request):
    return render(request,"index.html")

def purchase(request):
    current_user=request.user
    print(current_user)
    allProds=[]
    catprods= Product.objects.values("category",'id')
    cats={ item['category'] for item in catprods }
    for cat in cats:
        prod=Product.objects.filter(category=cat)
        n=len(prod)
        nSlides=n//4 + ceil((n/4)-(n//4))
        allProds.append([prod,range(1,nSlides),nSlides])
    
    params = { 'allProds':allProds}
    return render(request,"purchase.html", params)

def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login and try again.")
        return redirect('/auth/login')

    if request.method=="POST":
        items_json=request.POST.get("itemsJson",'')
        name=request.POST.get("name"," ")
        amount=request.POST.get("amt"," ")
        email=request.POST.get("email",'')
        address1=request.POST.get("address1","")
        address2=request.POST.get("address2","")
        city=request.POST.get("city","")
        state=request.POST.get("state","")
        zip_code=request.POST.get("zip_code","")
        phone=request.POST.get("phone","")


    # payment integration
        client = razorpay.Client(auth=( settings.KEY,  settings.SECREAT))

        DATA = {
                "amount":eval(amount)*100,
                "currency": "INR",
                "receipt": "receipt#1",
            }
           
        payment= client.order.create(data=DATA) 
       
        print("**********")
        print(payment)
        print("**********")
        mainid=payment['id']
        
        Order=Orders(items_json=items_json,name=name,amount=amount,email=email,address1=address1,address2=address2,city=city,state=state,zip_code=zip_code,phone=phone,razor_pay_order_id=mainid, paymentstatus="Not Paid")
        print(amount)
        Order.save()
        update=OrderUpdate(order_id=Order.order_id,update_desc="The order has been placed",razor_pay_order_id=mainid,paymentstatus="Not Paid",phone=phone)
        update.save()
        thank=True
        ordercontent=Orders.objects.all().values()

        context={
            "ordercontent":ordercontent,
            "payment" :payment,
            "alert":"Please click >> PAY from razorpay <<TO MAKE Transaction"

        } 
      
        return render(request,"checkout.html",context)

    #payment Intigrataion
    
    return render(request,"checkout.html")


def success(request,razorpay_payment_id,razorpay_order_id,razorpay_signature):
       
        Order=Orders.objects.get(razor_pay_order_id=razorpay_order_id)
        Order.razor_pay_payment_id=razorpay_payment_id
        Order.razor_pay_signature=razorpay_signature
        # Order.amountpaid=payment['amount']
        Order.paymentstatus="Paid"
        Order.save()

        Orderupdate=OrderUpdate.objects.get( order_id=Order.order_id)
        # Orderupdate.amountpaid=payment['amount']
        Orderupdate.paymentstatus="Paid"
        Orderupdate.save()
        
        totalorders=Orders.objects.get(razor_pay_order_id=razorpay_order_id)
        json_data = totalorders.items_json
        email=totalorders.email

        context={
            "totalorders":totalorders,
            "data":json_data,
            "razorpay_payment_id":razorpay_payment_id,
            "razorpay_order_id":razorpay_order_id,
            "razorpay_signature":razorpay_signature,
            "email":email,
         } 
        return render(request,"success.html",context)

def orders(request,email):
    order = Orders.objects.filter(email=email).values()
    context={
        "Order":order
    }
         
    return render(request,"orders.html",context)