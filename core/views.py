from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Logs, LogDetails, Wallet, Order, Cart, ViewLog, Contact, Transaction_History, Category, LogOrder, Shopviaclone22, DollarRate, Payment, Accsmtp, Verify_Payment, Bank_Account, ProfileDetails, SMSOrder, S2_Num, Country, Service, SMMCategory, Platform, SMMService, SMMOrder, APIs
from django.db.models import Sum, Count
import uuid
from backend.models import S2, All
from django.core.files.base import ContentFile
from userauths.models import User
import shortuuid
import requests
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.files.storage import default_storage
from django.core.files import File
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import os
from django.contrib import messages
import json
import hmac
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from django.http import JsonResponse
from collections import defaultdict
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# SMS Sections

@login_required    
def show_number(request):
    order = SMSOrder.objects.filter(user=request.user, status="Pending", type="S2", delete=False).order_by("-id")
    count = SMSOrder.objects.filter(user=request.user, status="Pending", type="S2", delete=False).count()
    pending = SMSOrder.objects.filter(status="Pending", type="S2", user=request.user).order_by("-id")
    completed = SMSOrder.objects.filter(status="Completed", type="S2", user=request.user).order_by("-id")[:15]
    s2 = S2_Num.objects.all()
    # upgrade = Upgrade.objects.last()
    
    user_balance = Wallet.objects.get(user=request.user)
    
    dollar_rate = DollarRate.objects.get(id=1)
    bal = float(user_balance.balance)
    percent = S2.objects.get(status=True)
    what_percent = percent.percentage

    rate = dollar_rate.rate

    # final_prices = []

    # for s in s2:
    #     cal_percentage = s.price
    #     real_percent = int(what_percent)/100
    #     price = float(cal_percentage) * float(real_percent)
    #     final_price = float(cal_percentage) + float(price)
    #     tfinal = float(final_price) * float(rate)
    #     final = round(tfinal, 2)
        
    #     # final = float(cal_percentage) * float(rate)

    #     final_prices.append({
    #         "name": s.name,
    #         "id": s.id,
    #         "key": s.key,
    #         "price": final,
    #     })
    
    final_prices = S2_Num.objects.all()
    
    context = {
        # "u": upgrade,
        "o": order,
        "count": count,
        "s2": final_prices,
        "bal": user_balance,
        "p": pending,
        "i": completed,
    }
    return render(request, "sms/buy.html", context)
    
@login_required
def order_s2_num(request):

    # {"data":{"order_id":51278,"number":"+14076249938","service":"Zoosk","status":"Reserved","state":"","markup":"10","price":"0.44","till_expiration":"2024-09-20 09:41:07"},"success":true,"summery":"Reserved"}

    key = request.GET["key"]
    # server = request.GET["server"]
    wallet = Wallet.objects.get(user=request.user)
    the_balance = wallet.balance
    balance = float(the_balance)
    
    check_if_key_exist = S2_Num.objects.filter(key=key).count()

    if check_if_key_exist:
        the_stuff = S2_Num.objects.get(key=key)
        # price = the_stuff.price
        dollar_rate = DollarRate.objects.get()
        percent = S2.objects.get(status=True)
        what_percent = percent.percentage

        rate = dollar_rate.rate
        cal_percentage = the_stuff.price
        real_percent = int(what_percent)/100
        price = float(cal_percentage) * float(real_percent)
        final_price = float(cal_percentage) + float(price)
        # final = float(final_price) * float(rate)
        final = float(the_stuff.price)
        name = the_stuff.name
        count_get_api_url = S2.objects.filter(status=True).count()
        
        if balance >= final:
            if count_get_api_url:
                get_api_url = S2.objects.get(status=True)
                api_key = get_api_url.api_key
                
                this_is_the_key = key
                
                the_url = get_api_url.order_api_url

                url = the_url + this_is_the_key
                
                # print(url)

                payload={
                    "api-key": api_key,
                    "service": key,
                }
                headers = {
                'Authorization': get_api_url.api_key,
                'Accept': 'application/json'
                }

                response = requests.request("GET", url, headers=headers, data=payload)

                print(response.text)

                preview = response.text

                # data = response.json()

                if "ACCESS_NUMBER" in preview:
                    if balance >= final:                        
                        charge_user = float(balance) - float(final)
                        wallet.balance = charge_user
                        wallet.save()
                        
                        the_number = preview.split(":")
                        the_id = the_number[1]
                        num = the_number[2]
                        create_order = SMSOrder.objects.create(
                            number_id=the_id,
                            user=request.user,
                            service=name,
                            key=key,
                            amount=final,
                            status="Pending",
                            profit=what_percent,
                            time=420,
                            type="S2",
                            phone_number=num,
                        )                                        

                        context = {
                            "bool": True,
                            "pre": preview,
                        }
                    else:
                        context = {
                            "bool": False,
                            "pre": preview,
                        }
                else:                                        
                    context = {
                        "bool": False,
                        "pre": preview,
                    }
        else:
            messages.error(request, "Sorry your balance is too low")
            return redirect("buy-number")
    return JsonResponse(context)

def reject_s2_number(request):
    wallet = Wallet.objects.get(user=request.user)
    s2_key = S2.objects.get(status=True)
    id = request.GET["id"]
    # the = request.GET["id"]
    codeorder = SMSOrder.objects.get(number_id=id)
    
    other = "&status=8"

    url = f"https://daisysms.com/stubs/handler_api.php?api_key={s2_key.api_key}&action=setStatus&id=" + codeorder.number_id + other

    payload={'order_id': codeorder.number_id}
    files=[]
    headers = {
    'Authorization': s2_key.api_key,
    'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload, files=files)

    print(response.text)
    
    view = response.text
    
    if "ACCESS_CANCEL" in view:
        check_order = SMSOrder.objects.get(number_id=id, status="Pending", delete=False)
        if not check_order.info:
            # check_order.delete()
            chnageo = SMSOrder.objects.filter(number_id=id).update(delete=True, status="Cancelled")
    
            order_amount = check_order.amount
            wallet_balance = wallet.balance
            refund_user = float(order_amount) + float(wallet_balance)
            wallet.balance = refund_user
            wallet.save()
    
        context = {
            "bool": True,
            "pre": view,
            # "url": url,
        }
    else:
        context = {
            "bool": False,
            "pre": view,
            # "url": url,
        }

    return JsonResponse(context)

def s2_code(request):
    key = request.GET["key"]
    number_id = request.GET["id"]
    the_api = S2.objects.get(status=True)
    
    the_url = the_api.code_api_url
    
    url = the_url + key

    payload={}
    files={}
    headers = {}
    
    response = requests.request("GET", url, headers=headers, data=payload, files=files)
    
    print(response.text)
    
    view = response.text
    
    
    if "STATUS_OK" in view:
        sms = view.split(":")
        code = sms[1]
        
        context = {
            "bool": True,
            "sms": code,
            "res": view,
        }
        
        check_order = SMSOrder.objects.filter(id=number_id).count()

        if check_order:
            the_order = SMSOrder.objects.get(id=number_id)
            the_order.info = code
            the_order.status = "Completed"
            the_order.save()
    else:
        context = {
            "bool": False,
            "res": view,
        }
        
    return JsonResponse(context)
    
def api_country(request):
    Country.objects.all().delete()
    url = "https://api.smspool.net/country/retrieve_all"

    payload={}
    files={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload, files=files)

    print(response.text)

    preview = response.text

    data = json.loads(preview)

    # dd = data.get("country")

    for country in data:        
        Country.objects.create(
            cid=country.get('ID', 0),
            name=country.get('name', "Unknown"),
            flag=country.get('short_name', 'Unknown')
        )

    context = {
        "bool": True,
        "pre": preview,
    }

    return JsonResponse(context)

def check_logo_url(url):
    try:
        res = requests.head(url, timeout=10)
        return res.status_code == 200
    except requests.RequestException:
        return False

def api_service(request):
    Service.objects.all().delete()
    url = "https://api.smspool.net/service/retrieve_all"

    payload={}
    files={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload, files=files)

    print(response.text)

    preview = response.text

    data = json.loads(preview)
    # dd = data.get("service")
    
    services_to_create = []

    for service in data:
        name = service.get('name', 'Unknown')
        domain_guess = name.lower().replace(' ', '')
        logo_url = service.get('flag', 'Unknown') 

        services_to_create.append(Service(
            sid=service.get('ID', 0),
            name=name,
            flag=logo_url
        ))

    Service.objects.bulk_create(services_to_create)    

    context = {
        "bool": True
    }

    return JsonResponse(context)
    
def order_all_num(request):
    api = All.objects.get(status=True)
    wallet = Wallet.objects.get(user=request.user)
    dprice = request.GET["price"]
    country = request.GET["country"]
    service = request.GET["service"]
    the_ser = Service.objects.get(sid=service)
    url = api.order_api_url    
    the_balance = Decimal(wallet.balance)    
    
    balance = float(the_balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    if wallet.vendor == True:
        ven = True
    else:
        ven = False

    payload={
        "key": api.api_key,
        "country": country,
        "service": service,
    }
    files=[]
    headers = {}
    
    if float(balance) >= float(dprice):
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        
        print(response.text)                        
        
        preview = response.text
        
        data = json.loads(preview)
        
        # data = response.json()
        
        if "success" in preview:
            cost = float(dprice)            
            charge_user = float(balance) - float(cost)
            wallet.balance = charge_user
            wallet.save()
            create_order = SMSOrder.objects.create(
                number_id=data.get('order_id', 0),
                user=request.user,
                service=the_ser.name,
                key=shortuuid.uuid(),
                amount=cost,
                profit=api.percentage,
                status="Pending",
                time=1200,
                type="All",
                vendor=ven,
                phone_number=data.get('number', 0),
            )
    
            context = {
                "bool": True,
                "message": "Purchased Successful",
                "pre": preview,
            }
        else:
            context = {
                "bool": False,
                "message": "No number found",
                "pre": preview,
            }
    else:
        context = {
            "message": "Insufficient Balance",
            "bool": "error",
            "pre": preview,
        }

    return JsonResponse(context)
    
def all_sms_cancel(request):
    api = All.objects.get(status=True)
    wallet = Wallet.objects.get(user=request.user)
    # id = request.GET["id"]
    id = request.GET["order_id"]
    
    order_id = SMSOrder.objects.get(id=id, status="Pending", delete=False).number_id

    url = "https://api.smspool.net/sms/cancel"

    payload={
        "orderid": order_id,
        "key": api.api_key,
    }
    files=[

    ]
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    print(response.text)

    preview = response.text

    data = json.loads(preview)

    if data.get('success') == 1:
        change_order = SMSOrder.objects.get(id=id, status="Pending", delete=False)
        if not change_order.info:
            # change_order.delete()
            chnageo = SMSOrder.objects.filter(id=id).update(delete=True, status="Cancelled")

            order_amount = change_order.amount
            wallet_balance = wallet.balance
            refund_user = float(order_amount) + float(wallet_balance)
            wallet.balance = refund_user
            wallet.save()

        context = {
            "bool": True,
            "message": "Success",
        }
    else:
        context = {
            "bool": False,
            "message": "Can't be cancelled now",
        }
    return JsonResponse(context)
    
def all_check_code(request):
    api = All.objects.get(status=True)
    id = request.GET["order_id"]

    url = api.code_api_url

    payload={
        "orderid": id,
        "key": api.api_key,
    }
    files=[]
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    print(response.text)

    preview = response.text

    data = json.loads(preview)

    error = data.get('errors')

    status = data.get('status')

    sms = data.get('sms')

    context = {
        "bool": preview,
        "error": error,
        "status": status,
        "sms": sms,
    }
    return JsonResponse(context)

def change_order_otp(request):
    number_id = request.GET["order_id"]
    pin = request.GET["pin"]
    check_order = SMSOrder.objects.filter(id=number_id).count()

    if check_order:
        the_order = SMSOrder.objects.get(id=number_id)
        the_order.info = pin
        the_order.status = "Completed"
        the_order.save()

        context = {
            "bool": True
        }

    else:
        context = {
            "bool": False
        }
    return JsonResponse(context)
    
def check_av_ajax(request):
    the_rate = DollarRate.objects.first()
    get_percent = All.objects.get(status=True)
    percent = get_percent.percentage
    user = Wallet.objects.get(user=request.user)
    bal = float(user.balance)
    # bal = ball
    can = None
    buy = None
    # upgrade = Upgrade.objects.last()


    country = request.GET["country"]
    service = request.GET["service"]
    
    get_service_name = Service.objects.get(sid=service).name

    url = "https://api.smspool.net/sms/all_stock"
    
    prurl = "https://api.smspool.net/request/price"

    payload={
        'country': country,
        'service': service,
        # 'pool': 7,
    }
    files=[]
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    prresponse = requests.request("POST", prurl, headers=headers, data=payload, files=files)
    
    review = prresponse.text

    prdata = json.loads(review)

    print(response.text)

    preview = response.text

    data = json.loads(preview)
    
    if data and isinstance(data[0], list) and data[0]:  
        dprice = prdata.get('high_price')
        for item in data[0]:  
            stock = item.get("stock", 0)  
            if stock > 0:
                break
    else:  
        dprice = 0  
        stock = 0  

    
    main_rate = the_rate.rate

    the_price = float(dprice) * float(main_rate)
    theuseremail = request.user.email
    
    
    
    finnaa = float(the_price)
    new_price_add = float(finnaa) + float(percent)    
    fina = float(finnaa) + float(percent)    
    final = round(fina, 2)
    
    if stock > 0:
        can = True
    else:
        can = False
        
    if bal >= final:
        buy = True
    else:
        buy = False


    context = {
        "data": data,
        "real": dprice,
        "price": final,
        "stock": stock,
        "bal": bal,
        "buy": buy,
        "can": can,
        "service": get_service_name,
    }
    return JsonResponse(context)
    
@login_required    
def numbers(request):
    numbers = SMSOrder.objects.filter(user=request.user, delete=False,).order_by("-date")
    
    context = {
        "num": numbers,
    }
    return render(request, "sms/numbers.html", context)
    
@login_required
def usa_purchased_number(request):
    numbers = SMSOrder.objects.filter(user=request.user, delete=False, status="Pending", type="S2").order_by("-date")[:10]
    
    context ={
        "p": numbers,
    }
    return render(request, "sms/usa-purchased-number.html", context)
    
@login_required
def all_purchased_number(request):
    numbers = SMSOrder.objects.filter(user=request.user, delete=False, status="Pending", type="All").order_by("-date")[:10]
    
    context ={
        "p": numbers,
    }
    return render(request, "sms/all-purchased-number.html", context)

def world(request):
    if not request.user.is_authenticated:
        return redirect("login")            
    current_user = request.user
    all_order = SMSOrder.objects.filter(user=request.user, status="Pending", type="All", delete=False).order_by("-id")
    country = Country.objects.all()
    service = Service.objects.all().order_by("name")
    api = All.objects.get(status=True)
    order = SMSOrder.objects.filter(user=request.user, status="Pending", type="All", delete=False)
    count = SMSOrder.objects.filter(user=request.user, status="Pending", type="All", delete=False).count()
    count_order = SMSOrder.objects.filter(user=request.user, delete=False).count()
    # deposit = Transaction_History.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum']
    bal = Wallet.objects.get(user=request.user)

    context = {
        "user": current_user,
        "all": all_order,
        "country": country,
        "o": order,
        "count": count,
        "service": service,
        "api": api,
        "count_order": count_order,
        # "deposit": deposit,
        "bal": bal,
    }
    return render(request, "sms/world.html", context)
  

# Log Section
@csrf_exempt  # Exempt CSRF for webhook-like endpoints
# @require_POST  # Restrict to POST requests
def verify_pocketfi_webhook(request):
    # Get the raw request payload
    payload = request.body.decode('utf-8')  # Decode bytes to string
    Verify_Payment.objects.create(
        key=payload,
    )
    # Get the signature from headers
    # pocketfi_signature = request.headers.get('POCKETFI-SIGNATURE')
    # Secret key (should ideally come from settings or environment)
    # secret = os.environ.get('POCKETFI_WEBHOOK_SECRET', '')
    # # Generate HMAC SHA512 hash
    # hashkey = hmac.new(
    #     secret.encode('utf-8'),  # Convert secret to bytes
    #     payload.encode('utf-8'),  # Convert payload to bytes
    #     hashlib.sha512
    # ).hexdigest()
    # Verify the signature
    # if pocketfi_signature and hmac.compare_digest(pocketfi_signature, hashkey):
    try:
        # Parse JSON payload
        data = json.loads(payload)
        # Extract data
        # amount = float(data['order']['amount'])
        settlement_amount = float(data['order']['settlement_amount'])
        fee = float(data['order']['fee'])
        reference = data['transaction']['reference']
        description = data['order']['description']
        email = data['customer']['email']
        # create_key = Verify_Payment.objects.create(key=data)
        amoun = float(settlement_amount)

        amount = float(amoun)
        
        user = User.objects.get(email=email)
        
        update_bal = Wallet.objects.get(user=user)
        old_bal = update_bal.balance
        print(old_bal)
        print("Flutterwave:", amount)
        chhc = float(old_bal)
        rounded_value = float(chhc)
        chc = float(amount)
        crounded_value = float(chc)
        new_bal = float(rounded_value) + float(crounded_value)
        print(new_bal)
        update_bal.balance = new_bal
        update_bal.save()
        
    
        log_it = Transaction_History.objects.create(
            user=user,
            email=email,
            amount=amount,
            status="Approved",
            # type="PocketFi",
        )
        # Return success response
        return JsonResponse({"message": "success"}, status=200)
    except (json.JSONDecodeError, KeyError) as e:
        # Handle invalid JSON or missing keys
        return JsonResponse({"message": f"Invalid payload: {str(e)}"}, status=400)
    # Return error response for invalid signature
    # return JsonResponse({"message": "Permission denied, invalid hash"}, status=400)

@csrf_exempt
@login_required
def pocketfi(request):
    user = request.user
    email = user.email
    name = user.username
    accnum = None
    accname = None
    if request.method == "POST":
        number = request.POST.get("number")
        dbank = request.POST.get("bank")
        # Your webhook URL
        url = "https://api.pocketfi.ng/api/v1/virtual-accounts/create"
    
        payload = {
            "phone": number,
            "first_name": name,
            "last_name": name,
            "email": email,    
            "businessId": "29697",
            "bank": dbank
        }
        headers = {
            "accept": "application/json",    
            "Authorization": "Bearer 11788|wR70W0ISBc32AbkUOGr1V3GSYJKAG2ZyTfg2VL65d406f53f",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        print(response.text)
        
        data = response.json()
        
        if data.get('status') == True:
            dstatus = True
            banks = data.get("banks")
        
            for bank in banks:
                bankname = bank["bankName"]
                accnum = bank["accountNumber"]
                accname = bank["accountName"]
                
                create_bank = Bank_Account.objects.create(
                    user=request.user,
                    bank_name=bankname,
                    account_name=accname,
                    account_number=accnum,
                )
                messages.success(request, "Account created successfully")
                return redirect("deposit")
        else:
            dstatus = False
            messages.error(request, f"{dbank} Account not available")
            return redirect("deposit")
            
    
    context = {
        "name": accname,
        "number": accnum,
        "wstatus": dstatus,
        "data": data,
    }
    
    return JsonResponse(context)


def paypoint(request):
    user = request.user
    email = user.email
    name = user.username
    accnum = None
    accname = None
    if request.method == "POST":
        number = request.POST.get("number")
        # Your webhook URL
        url = 'https://api.paymentpoint.co/api/v1/createVirtualAccount'
    
        data = {
            'email': email,
            'name': name,
            'phoneNumber': number,
            'bankCode': ['20946'],
            'businessId': '17bf49a3485ee4a1b48eeb68174ebb5b10b56,dc4',
        }
    
        # Headers if required (e.g., content type or authentication)
        headers = {
            'Authorization': 'Bearer 866f2a33a86d2f51770242cde6a87a69171ec84aad78f956569e065a53c07b2fbf6b91e9094cced01594e1b865f621a3eeaf04df98508a215b7daeed',
            'Content-Type': 'application/json',
            'api-key': '2d6a4e7ea023e0aef1442d4e3fca0fdecc29dc86',
        }
    
        # Sending the POST request to the webhook
        response = requests.post(url, json=data, headers=headers)
    
        # Print the response status and content
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    
        d = response.json()
    
        accnum = d['bankAccounts'][0]['accountNumber']
        accname = d['bankAccounts'][0]['accountName']
        bankname = d['bankAccounts'][0]['bankName']
        
        print(f"Name: {accname}")
        print(f"Number: {accnum}")
        
        if d.get('status') == "success":
            create_bank = Bank_Account.objects.create(
                user=request.user,
                bank_name=bankname,
                account_name=accname,
                account_number=accnum,
            )
            
            return redirect("deposit")
    
        context = {
            "name": accname,
            "number": accnum,
        }
    
    return JsonResponse(context)
    
@csrf_exempt  # Disable CSRF validation for the webhook (it's not necessary for webhooks)
def paypoint_webhook(request):
    # Get the raw JSON data from the request
    webhook_data = request.body  # Raw bytes, not text
    print("This is the webhook:", webhook_data)

    # Parse the incoming JSON data
    data = json.loads(webhook_data)

    # Extract relevant data
    transaction_id = data.get('transaction_id')
    amount_paid = data.get('amount_paid')
    settlement_amount = data.get('settlement_amount')
    status = data.get('transaction_status')
    email = data['customer']['email']

    # Process the data (e.g., store in DB, send email, etc.)
    print(f"Transaction ID: {transaction_id}")
    print(f"Amount Paid: {amount_paid}")
    print(f"Settlement Amount: {settlement_amount}")
    print(f"Status: {status}")
    print(f"Email: {email}")
    
    amount = float(settlement_amount)
    
    tr = Verify_Payment.objects.filter(key=transaction_id)
    
    if not tr:
        user = User.objects.get(email=email)
        
        update_bal = Wallet.objects.get(user=user)
        old_bal = update_bal.balance
        print(old_bal)
        print("Flutterwave:", amount)
        chhc = float(old_bal)
        rounded_value = round(chhc)
        chc = float(amount)
        crounded_value = round(chc)
        new_bal = int(rounded_value) + int(crounded_value)
        print(new_bal)
        update_bal.balance = new_bal
        update_bal.save()
        
        
        save_key = Verify_Payment.objects.create(
            key=transaction_id
        )
        
    
        log_it = Transaction_History.objects.create(
            user=user,
            email=email,
            amount=amount,
            status="Approved",
        )
    
    # Respond with a 200 OK status to acknowledge receipt of the webhook
    return JsonResponse({"status": "success"}, status=200)

@csrf_exempt
def enkpay_webhook(request):
    try:
        # Parse the JSON payload
        payload = json.loads(request.body)
        print("This is the payload:", payload)
    
        # Extract data
        # status = payload.get("status")
        email = payload.get("email")
        transaction_id = payload.get("order_id")
        amount = payload.get("amount")
    
        # Find the payment in your database
        try:
            payment = User.objects.get(email=email)
            wallet = Wallet.objects.get(user=payment)
            bal = wallet.balance
            check_key = Verify_Payment.objects.filter(key=transaction_id)
            
            if not check_key:
                total = float(bal) + float(amount)
                wallet.balance = float(total)
                wallet.save()
                
                save_key = Verify_Payment.objects.create(
                    key=transaction_id
                )
                
                log_it = Transaction_History.objects.create(
                    user=payment,
                    email=email,
                    amount=amount,
                    status="Approved",
                )
            else:
                return redirect("new")
            return JsonResponse({"message": "Payment processed successfully"}, status=True)
            # else:
            #     return JsonResponse({"message": "Payment failed"}, status=400)
        except Verify_Payment.DoesNotExist:
            return JsonResponse({"error": "Payment not found"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)


@login_required    
def point(request):
    banks = Bank_Account.objects.filter(user=request.user)
    current_user = request.user
    request.session['fund_wallet'] = True
    tx_ref = shortuuid.uuid()
    check = shortuuid.uuid()
    
    context = {
        "ref": tx_ref,
        "user": current_user,
        "check": check,
        "bank": banks,
    }
    return render(request, "core/payment-point.html", context)
    
def index(request):
    # if request.user.is_authenticated:
    #     check_wallet = Wallet.objects.filter(user=request.user).count()
    #     if check_wallet:
    #         pass
    #     else:
    #         create_wallet = Wallet.objects.create(
    #             user=request.user,
    #             email=request.user.email,
    #             balance=0,
    #         )
    # else:
    #     pass
    ig = Logs.objects.filter(category="instagram")
    ter = LogDetails.objects.filter(which_log__in=ig, used=False).count()
    fb_50 = Logs.objects.filter(category="facebook_50")
    fb_other = Logs.objects.filter(category="facebook_other")
    fb_dating = Logs.objects.filter(category="facebook_dating")
    fb_usa = Logs.objects.filter(category="facebook_usa")
    text = Logs.objects.filter(category="texting_numbers")
    tools = Logs.objects.filter(category="tools")
    twitter = Logs.objects.filter(category="twitter")
    vpn = Logs.objects.filter(category="vpn")
    reddit = Logs.objects.filter(category="reddit")
    tiktok = Logs.objects.filter(category="tiktok")
    mails = Logs.objects.filter(category="mails")
    cat_list = Category.objects.all()
    all_cat = Category.objects.prefetch_related('thelogs').all()
    # logs = Logs.objects.filter(category=all_cat)
    
    orders = Order.objects.all().order_by('-date')[:20]

    context = {
        "ig": ig,
        "ter": ter,
        "fb_50": fb_50,
        "fb_other": fb_other,
        "fb_dating": fb_dating,
        "fb_usa": fb_usa,
        "text": text,
        "tools": tools,
        "twitter": twitter,
        "vpn": vpn,
        "reddit": reddit,
        "tiktok": tiktok,
        "mails": mails,
        "all_cat": all_cat,
        "cat": cat_list,
        "order": orders,
    }
    return render(request, "core/old_index.html", context)
    
def new_index(request):
    if request.user.is_authenticated:
        wallet = Wallet.objects.get(user=request.user)
        balance = wallet.balance
        trans = Transaction_History.objects.filter(user=request.user).order_by('-date')[:10]
    else:
        balance = 0
        trans = None
        
    all_cat = Category.objects.prefetch_related('thelogs').all().order_by('-id')
    
    orders = Order.objects.all().order_by('-date')[:10]
    
    context = {
        "all_cat": all_cat,
        "order": orders,
        "trans": trans,
        "bale": balance,
    }
    return render(request, "core/index.html", context)
    
def totalpayment_ajax(request):
    id = request.GET["id"]
    amount = request.GET["amount"]
    
    check_id = Logs.objects.filter(id=id)
    if check_id:
        the_log = Logs.objects.get(id=id)
        price = the_log.price
        
        total = float(price) * float(amount)
    else:
        total = "Error"
        
    context = {
        "total": total
    }
    return JsonResponse(context)
    
def product_category(request, cid):
    if request.user.is_authenticated:
        wallet = Wallet.objects.get(user=request.user)
        balance = wallet.balance
        trans = Transaction_History.objects.filter(user=request.user).order_by('-date')[:10]
    else:
        balance = 0
        trans = None
    
    all_cat = Category.objects.prefetch_related('thelogs').all().order_by('-id')
    orders = Order.objects.all().order_by('-date')[:10]    
    check_first = Category.objects.filter(cid=cid).count()
    
    if check_first:
        get_cid = Category.objects.get(cid=cid)
        list_cat = Logs.objects.filter(cat=get_cid)
        
        context = {
            "bool": True,
            "cat": list_cat,
            "a": get_cid,
            "order": orders,
            "trans": trans,
            "bale": balance,
            "all_cat": all_cat,
        }
    else:
        context = {
            "bool": False,
            "order": orders,
            "trans": trans,
            "bale": balance,
        }
    return render(request, "core/product-category.html", context)
    
def product_view(request, id):
    check_first = Logs.objects.filter(id=id).count()
    
    if check_first:
        get_id = Logs.objects.get(id=id)
        context = {
            "bool": True,
            "product": get_id,
        }
        
        check = Cart.objects.filter(log=get_id, user=request.user).count()
    
        if check:
            pass
        else:
            count_clear = Cart.objects.filter(user=request.user).count()
            if count_clear:
                clear = Cart.objects.get(user=request.user)
                clear.delete()
                
                cart = Cart.objects.create(
                    user=request.user,
                    log=get_id,
                )
            else:
                cart = Cart.objects.create(
                    user=request.user,
                    log=get_id,
                )
    else:
        context = {
            "bool": False
        }
    return render(request, "core/product-view.html", context)


def popup(request):
    items = Cart.objects.filter(user=request.user)
    wallet = Wallet.objects.get(user=request.user)

    context = {
        "items": items,
        "wallet": wallet
    }
    return render(request, "core/popup.html", context)

def add_to_cart(request):
    id = request.GET["id"]
    add = Logs.objects.get(id=id)
    check = Cart.objects.filter(log=add, user=request.user).count()

    if check:
        context = {
            "bool": False
        }
    else:
        count_clear = Cart.objects.filter(user=request.user).count()
        if count_clear:
            clear = Cart.objects.get(user=request.user)
            clear.delete()
        else:
            pass
        cart = Cart.objects.create(
            user=request.user,
            log=add,
        )
        context = {
            "bool": True
        }
    return JsonResponse(context)

def order(request):
    id = request.GET["id"]
    lid = Logs.objects.filter(id=id).last()
    qty = request.GET["qty"]
    normal_price = float(lid.price) * float(qty)
    price = normal_price
    name = lid.name
    # category = request.GET["category"]
    new_q = int(qty)
    asset = Wallet.objects.get(user=request.user)
    balance = asset.balance

    if float(price) > float(balance):
        context = {
            "bool": False
        }
    else:
        check_cart = Logs.objects.filter(id=id).count()

        if check_cart:
            the_cart = Logs.objects.get(id=id)
            category = the_cart.cat
            check_for_details_count = LogDetails.objects.filter(which_log=the_cart, used=False).count()

            if check_for_details_count < new_q:
                context = {
                    "qty": False
                }
                
            else:
                context = {
                    "qty": True
                }
                check_for_details = LogDetails.objects.filter(which_log=the_cart, used=False)[:new_q]
                
                details = '\n'.join(f"{log_detail.details} *" for log_detail in check_for_details).rstrip(' * Next Log * ')
                # for d_info in check_for_details:
                #     theinfo = d_info.details
                
                change_bal = Wallet.objects.get(user=request.user)
                print("This is the balance:", change_bal.balance)
                print("This is the price:", price)
                new_bal = float(change_bal.balance) - float(price)
                print("New Balance:", new_bal)
                change_bal.balance = new_bal
                change_bal.save()

                the_order = Order.objects.create(
                    user=request.user,
                    email=request.user.email,
                    log=name,
                    category=category,
                    amount=price,
                    qty=qty,
                    info=details,
                )
                # check_for_details.used = True
                # check_for_details.save()
                
                services_to_create = []
                
                for d in check_for_details:
                    # different_log = LogOrder.objects.create(
                    #     user=request.user,
                    #     order=the_order,
                    #     log=d.details,
                    # )
                    
                    services_to_create.append(LogOrder(
                        user=request.user,
                        order=the_order,
                        log=d.details,
                    ))
                    
                    to_delete = ProfileDetails.objects.filter(which_log=the_cart)[:new_q]
                    for obj in to_delete:
                        obj.delete()
                    
                    d.used = True
                    # d.save()
            
                LogOrder.objects.bulk_create(services_to_create)
                LogDetails.objects.bulk_update(check_for_details, ['used'])

                new_qty = int(the_cart.qty)
                new_qty -= new_q
                the_cart.qty = str(new_qty)
                the_cart.save()
        else:
            pass
            context = {
                "bool": True
            }
    return JsonResponse(context)
    
    
def neworder(request, buy):
    if request.method == "POST":
        lid = Logs.objects.filter(id=buy).last()
        id = lid.id
        price = lid.price
        qty = request.POST.get("quantity")
        name = lid.name
        new_q = int(qty)
        asset = Wallet.objects.get(user=request.user)
        balance = asset.balance
    
        if float(price) > float(balance):
            messages.error(request, "error")
            return redirect("marketplace")
            context = {
                "bool": False
            }
        else:
            check_cart = Logs.objects.filter(id=id).count()
    
            if check_cart:
                the_cart = Logs.objects.get(id=id)
                category = the_cart.cat
                check_for_details_count = LogDetails.objects.filter(which_log=the_cart, used=False).count()
    
                if check_for_details_count < new_q:
                    messages.error(request, "qty")
                    return redirect("marketplace")
                    context = {
                        "qty": False
                    }
                    
                else:
                    messages.success(request, "success")
                    return redirect("marketplace")
                    context = {
                        "qty": True
                    }
                    check_for_details = LogDetails.objects.filter(which_log=the_cart, used=False)[:new_q]
                    
                    details = '\n'.join(f"{log_detail.details} *" for log_detail in check_for_details).rstrip(' * Next Log * ')
                    change_bal = Wallet.objects.get(user=request.user)
                    print("This is the balance:", change_bal.balance)
                    print("This is the price:", price)
                    new_bal = float(change_bal.balance) - float(price)
                    print("New Balance:", new_bal)
                    change_bal.balance = new_bal
                    change_bal.save()
    
                    the_order = Order.objects.create(
                        user=request.user,
                        email=request.user.email,
                        log=name,
                        category=category,
                        amount=price,
                        qty=qty,
                        info=details,
                    )
                    
                    services_to_create = []
                    
                    for d in check_for_details:
                        services_to_create.append(LogOrder(
                            user=request.user,
                            order=the_order,
                            log=d.details,
                        ))
                        
                        d.used = True
                
                    LogOrder.objects.bulk_create(services_to_create)
                    LogDetails.objects.bulk_update(check_for_details, ['used'])
    
                    new_qty = int(the_cart.qty)
                    new_qty -= new_q
                    the_cart.qty = str(new_qty)
                    the_cart.save()
            else:
                messages.success(request, "avi")
                return redirect("marketplace")
                pass
                context = {
                    "bool": True
                }
    return JsonResponse(context)

def order_email(request):
    # email_template = render_to_string('partials/order-email.html')

    # email_send = EmailMessage(
    #     'Logsplace Admin Order Notification',
    #     email_template,
    #     'info@logsplace.com',
    #     ['opemummy466@gmail.com', 'teniolamail@gmail.com'],
    # )

    # email_send.fail_silently=False
    # email_send.content_subtype == "html"
    # email_send.send()
    
    return JsonResponse

@login_required
def account(request):
    count_orders = Order.objects.filter(user=request.user).count()
    balance = Wallet.objects.get(user=request.user)
    spent = Order.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum']
    trans = Transaction_History.objects.filter(user=request.user).order_by('-date')

    print(spent)

    if spent == None:
        bal = "0"
    else:
        bal = spent

    context = {
        "orders": count_orders,
        "bal": balance,
        "spent": bal,
        "trans": trans,
    }
    return render(request, "core/account.html", context)
    
@login_required
def dashboard(request):
    count_orders = Order.objects.filter(user=request.user).count()
    balance = Wallet.objects.get(user=request.user)
    spent = Order.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum']
    trans = Transaction_History.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    transa = Transaction_History.objects.filter(user=request.user).order_by('-date')
    username = request.user.username[:1]

    print(spent)

    if spent == None:
        bal = "0"
    else:
        bal = spent

    context = {
        "orders": count_orders,
        "bal": balance,
        "spent": bal,
        "trans": trans,
        "t": transa,
        "u": username,
    }
    return render(request, "core/dashboard.html", context)

# @login_required
def marketplace(request):
    mcategory = Category.objects.annotate(log_count=Count('thelogs'))
    apilogs = Logs.objects.filter(from_api=True)
    acclogs = Logs.objects.filter(from_acc=True)
    logs = Logs.objects.filter(from_acc=False, from_api=False)
    
    if request.method == "POST":
        category = request.POST.get("category")
        min_price = request.POST.get("min_price")
        max_price = request.POST.get("max_price")
        search = request.POST.get("search")
        
        if search:
            apilogs = Logs.objects.filter(name__icontains=search, from_api=True)
            acclogs = Logs.objects.filter(name__icontains=search, from_acc=True)
            logs = Logs.objects.filter(name__icontains=search, from_acc=False, from_api=False)
        
        if category:
            gcategory = Category.objects.filter(id=category).last()
            apilogs = Logs.objects.filter(cat=gcategory, from_api=True)
            acclogs = Logs.objects.filter(cat=gcategory, from_acc=True)
            logs = Logs.objects.filter(cat=gcategory, from_acc=False, from_api=False)
    
    context = {
        "c": mcategory,
        "l": apilogs,
        "o": acclogs,
        "log": logs,
    }
    return render(request, "core/marketplace.html", context)

@login_required
def deposit(request):
    if request.user.is_authenticated:
        balanc = Wallet.objects.get(user=request.user)
        balance = balanc.balance
    else:
        balance = None
        
    request.session['fund_wallet'] = True
    amount = request.POST.get('amount')
    print("Line 297:", amount)
    request.session['amount'] = amount
    tx_ref = shortuuid.uuid()
    trans = Transaction_History.objects.filter(user=request.user).order_by('-date')
    banks = Bank_Account.objects.filter(user=request.user).last()

    context = {
        "ref": tx_ref,
        "trans": trans,
        "bale": balance,
        "b": banks,
    }
    return render(request, "core/deposit.html", context)
    
@login_required
def deposit_p(request):
    all_cat = Category.objects.prefetch_related('thelogs').all()
    if request.user.is_authenticated:
        balanc = Wallet.objects.get(user=request.user)
        balance = balanc.balance
    else:
        balance = None
        
    request.session['fund_wallet'] = True
    amount = request.POST.get('amount')
    print("Line 297:", amount)
    request.session['amount'] = amount
    tx_ref = shortuuid.uuid()
    trans = Transaction_History.objects.filter(user=request.user).order_by('-date')

    context = {
        "ref": tx_ref,
        "trans": trans,
        "bale": balance,
        "all_cat": all_cat,
    }
    return render(request, "core/flutterwave.html", context)
    
@login_required
def enkpay(request):
    api = "44995584945435"
    all_cat = Category.objects.prefetch_related('thelogs').all()
    if request.user.is_authenticated:
        balanc = Wallet.objects.get(user=request.user)
        balance = balanc.balance
    else:
        balance = None
        
    request.session['fund_wallet'] = True
    amount = request.POST.get('amount')
    print("Line 297:", amount)
    request.session['amount'] = amount
    tx_ref = shortuuid.uuid()
    trans = Transaction_History.objects.filter(user=request.user).order_by('-date')
    email = request.user.email
    if request.method == "POST":
        return redirect(f"https://web.sprintpay.online/pay?amount={amount}&key={api}&ref={tx_ref}&email={email}")

    context = {
        "ref": tx_ref,
        "trans": trans,
        "bale": balance,
        "all_cat": all_cat,
    }
    return render(request, "core/enkpay.html", context)

def deposit_amount(request):

    print("This is from Deposit Amount Check")
    amount = request.GET["amount"]

    if amount:
        # request.session['amount'] = amount
        # print("This is the amount to pass:", amount)
        # sess = request.session.get('amount')
        # print("This is the amount in session:", sess)
        
        update_to_pay = Wallet.objects.get(user=request.user)
        update_to_pay.to_add = amount
        update_to_pay.save()

        context = {
            "bool": True
        }
    else:
        context = {
            "bool": False
        }
    return JsonResponse(context)
    
def test(request):
    add_zero = Wallet.objects.all()
    for d in add_zero:
        d.to_add = "0"
        d.save()
        
def paystack_redirect(request):
    if request.user.is_authenticated:
        balanc = Wallet.objects.get(user=request.user)
        balance = balanc.balance
    else:
        balance = None
    if request.method == "POST":
        email = request.POST.get('email')  # Get user email from the form
        amount = int(request.POST.get('amount')) * 100  # Convert to kobo
        
        # Prepare Paystack payload
        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {os.environ.get('PAYSTACK_SECRET_KEY', '')}",
            "Content-Type": "application/json"
        }
        payload = {
            "email": email,
            "amount": amount,
            "callback_url": ("https://logsplace.com/paystack-verify/")
        }

        # Make request to Paystack
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()

        if result['status']:
            # Redirect the user to the payment page
            payment_url = result['data']['authorization_url']
            return redirect(payment_url)
        else:
            # Handle error
            return render(request, 'payment_failed.html', {'error': result.get('message', 'An error occurred')})
    return render(request, "core/paystack-redirect.html", {"bale": balance,})
    
def paystack_verify(request):
    paystack_secret_key = os.environ.get('PAYSTACK_SECRET_KEY', '')
    reference = request.GET.get("reference")
    damount = float(1000)

    if not reference:
        return JsonResponse({'status': 'error', 'message': 'No reference provided'}, status=400)

    # Paystack API endpoint for verification
    url = f"https://api.paystack.co/transaction/verify/{reference}"

    # Set up the headers
    headers = {
        "Authorization": f"Bearer {paystack_secret_key}"
    }

    # Make the request to Paystack
    response = requests.get(url, headers=headers)
    data = response.json()

    if response.status_code == 200 and data.get('status') == True:
        aount = data['data']['amount']
        amount = float(aount) / 100
        
        update_bal = Wallet.objects.get(user=request.user)
        old_bal = update_bal.balance
        print(old_bal)
        print("Flutterwave:", amount)
        chhc = float(old_bal)
        rounded_value = round(chhc)
        chc = float(amount)
        crounded_value = round(chc)
        new_bal = int(rounded_value) + int(crounded_value)
        print(new_bal)
        update_bal.balance = new_bal
        update_bal.save()
        
        # the_id = Verify_Payment.objects.create(
        #     key=transaction_id
        # )

        log_it = Transaction_History.objects.create(
            user=request.user,
            feedback=request.user.email,
            amount=amount,
            status="Approved",
        )
        # Payment verified successfully
        # payment_data = data.get('data', {})
        # return JsonResponse({
        #    'status': 'success',
        #    'message': 'Payment verified successfully',
        #    'data': payment_data,
        #    'amount': amount,
        #
        return redirect("new")
    else:
        log_it = Transaction_History.objects.create(
            user=request.user,
            feedback=request.user.email,
            amount=amount,
            status="Declined",
        )
        # Payment verification failed
        #return JsonResponse({
        #    'status': 'error',
        #    'message': response_data.get('message', 'Payment verification failed')
        #}, status=400)
        return redirect("deposit")
    return render(request, "core/payment.html")
        
        
def payment_check(request):
    # amount = request.session.get('amount')
    # to_pay = Wallet.objects.get(user=request.user)
    # amount = to_pay.to_add
    status = request.GET.get('status')
    
    transaction_id = request.GET.get('transaction_id')
    pay = Payment.objects.filter(transaction_id=transaction_id).count()

    url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
    headers = {
        "Authorization": f"Bearer FLWSECK-43bdf2efddda175f0a0f230395d1d805-1942a5ac7cbvt-X"
    }
    response = requests.get(url, headers=headers)
    
    
    # print(response.text)
    
    if response.status_code == 200:
        if pay:
            return redirect("deposit")
        data = response.json()
        if data.get('status') == "success":
            amount = data['data']['amount']
            currency = data['data']['currency']
            customer_email = data['data']['customer']['email']
            
            update_bal = Wallet.objects.get(user=request.user)
            old_bal = update_bal.balance
            print(old_bal)
            print("Flutterwave:", amount)
            chhc = float(old_bal)
            rounded_value = round(chhc)
            chc = float(amount)
            crounded_value = round(chc)
            new_bal = int(rounded_value) + int(crounded_value)
            print(new_bal)
            update_bal.balance = new_bal
            update_bal.save()
            
            the_id = Payment.objects.create(
                transaction_id=transaction_id
            )
    
            log_it = Transaction_History.objects.create(
                user=request.user,
                email=request.user.email,
                amount=amount,
                status="Approved",
            )
            
            this = Wallet.objects.get(user=request.user)
            this.to_add = "0"
            this.save()
        
        

            return redirect('new')
    else:
        print("Failed")

        log_it = Transaction_History.objects.create(
            user=request.user,
            email=request.user.email,
            amount=amount,
            status="Declined",
        )
        
        this = Wallet.objects.get(user=request.user)
        this.to_add = "0"
        this.save()

        return redirect('deposit')
    return render(request, "core/payment.html")

def search(request):
    query = request.GET.get("q")

    product = Logs.objects.filter(name__icontains=query)

    context = {
        "log": product,
        "q": query,
    }

    return render(request, "core/search.html", context)

@login_required
def all_order(request):
    my_order = Order.objects.filter(user=request.user).order_by('-id')
    count_orders = Order.objects.filter(user=request.user).count()
    balanc = Wallet.objects.get(user=request.user)
    balance = balanc.balance
    spent = Order.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum']
    all_cat = Category.objects.prefetch_related('thelogs').all()
    trans = Transaction_History.objects.filter(user=request.user).order_by('-date')
    
    
    
    if spent == None:
        bal = "0"
    else:
        bal = spent

    context = {
        "orders": count_orders,
        "bale": balance,
        "spent": bal,
        "trans": trans,
        "my_orders": my_order,
        "all_cat": all_cat,
    }
    return render(request, "core/orders.html", context)

@login_required
def history(request):
    all_cat = Category.objects.prefetch_related('thelogs').all()
    if request.user.is_authenticated:
        balanc = Wallet.objects.get(user=request.user)
        balance = balanc.balance
        trans = Transaction_History.objects.filter(user=request.user).order_by('-date')
        orders = Order.objects.filter(user=request.user).order_by('-date')
    else:
        balance = None
        trans = None
        
    context = {
        "bale": balance,
        "trans": trans,
        "all_cat": all_cat,
        "o": orders,
    }
    return render(request, "core/history.html", context)
    
def view_order(request, id):
    if request.user.is_authenticated:
        balanc = Wallet.objects.get(user=request.user)
        balance = balanc.balance
        check_order = Order.objects.filter(id=id, user=request.user).count()
        all_cat = Category.objects.prefetch_related('thelogs').all()
        
        if check_order:
            # the_log = Order.objects.get(id=id)
            log_ord = Order.objects.get(id=id)
            log_order = LogOrder.objects.filter(order=log_ord)
            
            context = {
                "bool": True,
                "log": log_ord,
                "bale": balance,
                "logs": log_order,
                "all_cat": all_cat,
            }
        else:
            context = {
                "bool": False,
                "bale": None
            }
    else:
        return redirect('login')
    return render(request, "core/order-view.html", context)

def check_log(request):
    id = request.GET['id']

    add = Order.objects.get(id=id)
    check = ViewLog.objects.filter(log=add, user=request.user).count()

    if check:
        context = {
            "bool": False
        }
    else:
        count_clear = ViewLog.objects.filter(user=request.user).count()
        if count_clear:
            clear = ViewLog.objects.get(user=request.user)
            clear.delete()
        else:
            pass
        cart = ViewLog.objects.create(
            user=request.user,
            log=add,
        )
        context = {
            "bool": True
        }
    return JsonResponse(context)

def view_log(request):
    log = ViewLog.objects.filter(user=request.user)

    context = {
        "items": log
    }
    return render(request, "core/view-log.html", context)

def contact(request):
    all_cat = Category.objects.all()
    if request.user.is_authenticated:
        balanc = Wallet.objects.get(user=request.user)
        balance = balanc.balance
    else:
        balance = None
        
    context = {
        "bale": balance,
        "all_cat": all_cat,
    }
    return render(request, "core/contact.html")

def contact_form(request):
    name = request.GET['name']
    email = request.GET['email']
    subject = request.GET['subject']
    message = request.GET['message']

    if name and email and subject and message:
        create_it = Contact.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message,
        )

        context = {
            "bool": True
        }
    else:
        context = {
            "bool": False
        }
    return JsonResponse(context)

def about(request):
    return render(request, "core/about.html")
    
def rules(request):
    return render(request, "core/rules.html")

def why(request):
    return render(request, "core/why.html")

@csrf_exempt    
def api_account_list(request):
    logs = Logs.objects.filter(from_api=True)
    delete_cat = Category.objects.filter(from_api=True)
    
    logs.delete()
    delete_cat.delete()
    details = Shopviaclone22.objects.get(id=1)
    dollar = DollarRate.objects.get(id=1)
    rate = dollar.rate
    username = details.username
    passw = details.password
    tty = details.percentage
    percentage = float(tty)
            
    url = f"https://shopviaclone22.com/api/products.php?api_key={details.username}"
    
    payload={}
    headers = {}
    
    response = requests.request("GET", url, headers=headers, data=payload)
    
    res = response.text
    
    data = response.json()


    categories = data.get("categories", [])
    for category in categories:
        category_name = category.get("name", "Unknown Category")
        category_id = category.get("id", "Unknown Category")
        category_icon = category.get("icon", "https://logsplace.com/shopviaclone22.com/assets/storage/images/logo_dark_BUP.png")
        # print(f"Category: {category_name}")
        # print(f"    ID: {category_id}")
        
        if category_id == "77":
            continue
        
        if category_id == "86":
            continue
        
        create_cat = Category.objects.create(
            name=category_name,
            image=category_icon,
            from_api=True,
        )
    
        accounts = category.get("products", [])
        for account in accounts:
            account_name = account.get("name", "Unknown Account")
            account_price = account.get("price", "Unknown Price")
            naira_price = float(account_price) * float(rate)
            increase = (percentage / 100) * naira_price
            new_val = float(naira_price) + float(percentage)
            new_value = round(new_val)
            account_description = account.get("description", "No Description")
            account_id = account.get("id", "No Description")
            account_amount = account.get("amount", "No Description")
            account_country = account.get("country", "No Description")
            # print(f"  Account: {account_name}")
            # print(f"    Price: {naira_price}")
            # print(f"    Description: {account_description}")
            # print(f"    ID: {account_id}")
            # print(f"    Amount: {account_amount}")
            # print(f"    Country: {account_country}")
            # print("-" * 50)
            
            create_log = Logs.objects.create(
                name=account_name,
                cat=create_cat,
                from_api=True,
                api_id=account_id,
                country=account_country,
                qty=account_amount,
                price=new_value,
            )
            
            # delete_vpn = Category.objects.get(cat_id=9)
            # delete_vpn.delete()

    
    # print(response.text)
    
    context = {
        "list": res,
    }
    return JsonResponse(context)

@csrf_exempt
def accsmtp_account_list(request):
    logs = Logs.objects.filter(from_acc=True)
    delete_cat = Category.objects.filter(from_acc=True)
    
    details = Accsmtp.objects.get(id=1)
    dollar = DollarRate.objects.get(id=1)
    rate = dollar.rate
    username = details.username
    passw = details.password
    tty = details.percentage
    percentage = float(tty)
            
    url = f"https://accsmtp.com/api/ListResource.php?username={details.username}&password={details.password}"
    
    payload={}
    headers = {}
    
    response = requests.request("GET", url, headers=headers, data=payload)
    
    # res = response.text
    res = response.text.replace("\n", "").replace("\\n", "")
    
    data = response.json()


    categories = data.get("categories", [])
    logs.delete()
    delete_cat.delete()
    for category in categories:
        category_name = category.get("name", "Unknown Category")
        category_id = category.get("id", "Unknown Category")
        category_icon = category.get("image", "https://logsplace.com/shopviaclone22.com/assets/storage/images/logo_dark_BUP.png")
        if category_id == "27":
            continue
        
        if category_id == "26":
            continue
        
        if category_id == "53":
            continue
        
        if category_id == "14":
            continue
        
        if category_id == "11":
            continue
        
        # print(f"Category: {category_name}")
        # print(f"    ID: {category_id}")
        
        create_cat = Category.objects.create(
            name=category_name,
            image=category_icon,
            from_acc=True,
        )
    
        accounts = category.get("accounts", [])
        for account in accounts:
            account_name = account.get("name", "Unknown Account")
            account_price = account.get("price", "Unknown Price")
            # increase = (percentage / 100) * float(account_price)
            # new_value = float(account_price) + increase
            # new_val = float(new_value) / 23000
            # new_price = float(new_val) * float(rate)
            
            # Add 1500 to balance
            convert = float(account_price) / 23000
            naira = float(convert) * float(rate)
            # round_it = round(convert)
            adde = float(naira) + (percentage)
            add = round(adde)
            
            account_description = account.get("description", "No Description")
            account_id = account.get("id", "No Description")
            account_amount = account.get("amount", "No Description")
            account_country = account.get("country", "No Description")
            # print(f"  Account: {account_name}")
            # print(f"    Price: {naira_price}")
            # print(f"    Description: {account_description}")
            # print(f"    ID: {account_id}")
            # print(f"    Amount: {account_amount}")gh
            # print(f"    Country: {account_country}")
            # print("-" * 50)
            
            
            create_log = Logs.objects.create(
                name=account_name,
                cat=create_cat,
                from_acc=True,
                api_id=account_id,
                country=account_country,
                qty=account_amount,
                price=add,
            )
    
    context = {
        "list": data,
        "message": "Update Successfully",
        "status": "success",
    }
    return JsonResponse(context)

# @csrf_exempt
# def accsmtp_account_list(request):
#     try:
#         # Delete old entries
#         Logs.objects.filter(from_acc=True).delete()
#         Category.objects.filter(from_acc=True).delete()

#         # Get account and rate details
#         details = Accsmtp.objects.get(id=1)
#         dollar = DollarRate.objects.get(id=1)
#         rate = dollar.rate
#         percentage = float(details.percentage)

#         # Fetch from API
#         url = f"https://accsmtp.com/api/ListResource.php?username={details.username}&password={details.password}"
#         try:
#             response = requests.get(url, timeout=30)
#             response.raise_for_status()
#             data = response.json()
#         except requests.RequestException as e:
#             return JsonResponse({"status": "error", "message": f"API request failed: {e}"}, status=500)

#         # Filtered category IDs to skip
#         excluded_ids = {"11", "14", "26", "27", "53"}

#         # Prepare for bulk create
#         category_objects = []
#         category_data = []

#         for category in data.get("categories", []):
#             cat_id = category.get("id")
#             if cat_id in excluded_ids:
#                 continue

#             name = category.get("name", "Unknown Category")
#             image = category.get("image") or "https://logsplace.com/shopviaclone22.com/assets/storage/images/logo_dark_BUP.png"

#             cat_obj = Category(name=name, image=image, from_acc=True)
#             category_objects.append(cat_obj)
#             category_data.append((name, category.get("accounts", [])))  # Store accounts for later

#         # Bulk insert categories
#         Category.objects.bulk_create(category_objects)

#         # Fetch created categories for mapping
#         category_map = {cat.name: cat for cat in Category.objects.filter(from_acc=True)}

#         # Prepare logs for bulk insert
#         log_objects = []
#         for name, accounts in category_data:
#             cat_instance = category_map.get(name)
#             for account in accounts:
#                 try:
#                     price = float(account.get("price", 0))
#                 except (ValueError, TypeError):
#                     price = 0

#                 naira = ((price / 23000) * rate) + percentage
#                 final_price = round(naira)

#                 log = Logs(
#                     name=account.get("name", "Unknown Account"),
#                     cat=cat_instance,
#                     from_acc=True,
#                     api_id=account.get("id", ""),
#                     country=account.get("country", ""),
#                     qty=account.get("amount", ""),
#                     price=final_price,
#                 )
#                 log_objects.append(log)

#         # Bulk insert logs
#         Logs.objects.bulk_create(log_objects)

#         return JsonResponse({
#             "list": response.text,
#             "message": "Update Successfully",
#             "status": "success"
#         })

#     except Exception as e:
#         return JsonResponse({
#             "status": "error",
#             "message": f"An unexpected error occurred: {e}"
#         }, status=500)
    
def buy_api_account(request):
    id = request.GET["id"]
    lid = Logs.objects.filter(id=id).last()
    qty = request.GET["qty"]
    normal_price = float(lid.price) * float(qty)
    price = normal_price
    name = lid.name
    # category = request.GET["category"]
    new_q = int(qty)
    asset = Wallet.objects.get(user=request.user)
    balance = asset.balance
    details = Shopviaclone22.objects.get(id=1)

    if float(price) > float(balance):
        context = {
            "bool": False
        }
    else:
        check_cart = Logs.objects.filter(id=id).count()

        if check_cart:
            the_cart = Logs.objects.get(id=id)
            category = the_cart.cat
            api_id = the_cart.api_id
            
            url = "https://shopviaclone22.com/api/buy_product"
            
            params = {
                "action": "buyProduct",
                "id": api_id,
                "amount": qty,
                "api_key": details.username,
            }
            
            response = requests.get(url, params=params)
            
            res = response.text
            
            data = response.json()
            
            print(response.text)
            

            # Check the status
            if data.get('status') == 'success':
                change_bal = Wallet.objects.get(user=request.user)
                print("This is the balance:", change_bal.balance)
                print("This is the price:", price)
                value = float(price)
                rounded_value = round(value)
                new_bal = float(change_bal.balance) - float(rounded_value)
                print("New Balance:", new_bal)
                change_bal.balance = new_bal
                change_bal.save()
                
                the_d = True
                # Loop through the accounts
                output = " * Next Log * ".join(data['data'])
                
                the_order = Order.objects.create(
                    user=request.user,
                    email=request.user.email,
                    log=name,
                    category=category,
                    amount=price,
                    qty=qty,
                    info=output,
                )
            else:
                the_d = False
                
            services_to_create = []
            
            if data.get('status') == 'success':
            # Loop through the accounts
                for item in data['data']:
                    print(item)
                    
                    # different_log = LogOrder.objects.create(
                    #     user=request.user,
                    #     order=the_order,
                    #     log=item,
                    # )
                    
                    services_to_create.append(LogOrder(
                        user=request.user,
                        order=the_order,
                        log=item,
                    ))
            
                LogOrder.objects.bulk_create(services_to_create)
                    
            # for d in check_for_details:

                new_qty = int(the_cart.qty)
                new_qty -= new_q
                the_cart.qty = str(new_qty)
                the_cart.save()
            
            context = {
                "list": res,
                "done": the_d,
            }
            
        else:
            pass
            context = {
                "bool": True,
                "list": False,
                "done": True,
            }
    return JsonResponse(context)

def clone_buy_api_account(request):
    id = request.GET["id"]
    lid = Logs.objects.filter(id=id).last()
    qty = request.GET["qty"]
    normal_price = float(lid.price) * float(qty)
    price = normal_price
    name = lid.name
    # category = request.GET["category"]
    new_q = int(qty)
    asset = Wallet.objects.get(user=request.user)
    balance = asset.balance
    details = Clonevn.objects.get(id=1)

    if float(price) > float(balance):
        context = {
            "bool": False
        }
    else:
        check_cart = Logs.objects.filter(id=id).count()

        if check_cart:
            the_cart = Logs.objects.get(id=id)
            category = the_cart.cat
            api_id = the_cart.api_id
            
            url = "https://shopclone.vn/api/buy_product"
            
            params = {
                "action": "buyProduct",
                "id": api_id,
                "amount": qty,
                "api_key": details.username,
            }
            
            response = requests.get(url, params=params)
            
            res = response.text
            
            data = response.json()
            
            print(response.text)
            

            # Check the status
            if data.get('status') == 'success':
                change_bal = Wallet.objects.get(user=request.user)
                print("This is the balance:", change_bal.balance)
                print("This is the price:", price)
                value = float(price)
                rounded_value = round(value)
                new_bal = float(change_bal.balance) - float(rounded_value)
                print("New Balance:", new_bal)
                change_bal.balance = new_bal
                change_bal.save()
                
                the_d = True
                # Loop through the accounts
                output = " * Next Log * ".join(data['data'])
                
                the_order = Order.objects.create(
                    user=request.user,
                    email=request.user.email,
                    log=name,
                    category=category,
                    amount=price,
                    qty=qty,
                    info=output,
                )
            else:
                the_d = False
                
            services_to_create = []
            
            if data.get('status') == 'success':
            # Loop through the accounts
                for item in data['data']:
                    print(item)
                    
                    # different_log = LogOrder.objects.create(
                    #     user=request.user,
                    #     order=the_order,
                    #     log=item,
                    # )
                    
                    services_to_create.append(LogOrder(
                        user=request.user,
                        order=the_order,
                        log=item,
                    ))
            
                LogOrder.objects.bulk_create(services_to_create)
                    
            # for d in check_for_details:

                new_qty = int(the_cart.qty)
                new_qty -= new_q
                the_cart.qty = str(new_qty)
                the_cart.save()
            
            context = {
                "list": res,
                "done": the_d,
            }
            
        else:
            pass
            context = {
                "bool": True,
                "list": False,
                "done": True,
            }
    return JsonResponse(context)
    
def acc_buy_api_account(request):
    id = request.GET["id"]
    lid = Logs.objects.filter(id=id).last()
    qty = request.GET["qty"]
    normal_price = float(lid.price) * float(qty)
    price = normal_price
    name = lid.name
    new_q = int(qty)
    asset = Wallet.objects.get(user=request.user)
    balance = asset.balance
    details = Accsmtp.objects.get(id=1)

    if float(price) > float(balance):
        context = {
            "bool": False
        }
    else:
        check_cart = Logs.objects.filter(id=id).count()

        if check_cart:
            the_cart = Logs.objects.get(id=id)
            category = the_cart.cat
            api_id = the_cart.api_id
            
            url = f"https://accsmtp.com/api/BResource.php?username={details.username}&password={details.password}&id={api_id}&amount={new_q}"

            payload={}
            headers = {}
            
            response = requests.request("GET", url, headers=headers, data=payload)
            
            
            print(response.text)
            
            data = response.json()
            

            # Check the status
            if data.get('status') == 'success':
                change_bal = Wallet.objects.get(user=request.user)
                print("This is the balance:", change_bal.balance)
                print("This is the price:", price)
                value = float(price)
                rounded_value = round(value)
                new_bal = float(change_bal.balance) - float(rounded_value)
                print("New Balance:", new_bal)
                change_bal.balance = new_bal
                change_bal.save()
                
                
                the_d = True
                # Loop through the accounts
                output = data['data']['lists']
                
                the_order = Order.objects.create(
                    user=request.user,
                    email=request.user.email,
                    log=name,
                    category=category,
                    amount=price,
                    qty=qty,
                    info=output,
                )
            else:
                the_d = False
                
            services_to_create = []
            
            if data.get('status') == 'success':
            # Loop through the accounts
                for item in data['data']['lists']:
                    print(item['account'])
                    loop = item['account']
                    
                    # different_log = LogOrder.objects.create(
                    #     user=request.user,
                    #     order=the_order,
                    #     log=loop,
                    # )
                    
                    services_to_create.append(LogOrder(
                        user=request.user,
                        order=the_order,
                        log=loop,
                    ))
            
                LogOrder.objects.bulk_create(services_to_create)
                    
            # for d in check_for_details:

                new_qty = int(the_cart.qty)
                new_qty -= new_q
                the_cart.qty = str(new_qty)
                the_cart.save()
            
            context = {
                "list": data,
                "done": the_d,
            }
            
        else:
            pass
            context = {
                "bool": True,
                "list": False,
                "done": True,
            }
    return JsonResponse(context)
    
def api_balance(request):
    details = Shopviaclone22.objects.get(id=1)
    # url = f"https://shopviaclone22.com/api/profile.php?api_key={details.username}"
    
    url = f"https://shopviaclone22.com/api/profile.php?api_key={details.username}"

    payload={}
    headers = {}
    
    response = requests.request("GET", url, headers=headers, data=payload)
    
    data = response.json()
    
    mone = data["data"]["money"]

    money = "$" + mone
    
    print(money)
    
    details.balance = money
    details.save()
    
    context = {
        "list": money,
    }
    return JsonResponse(context)
    
@csrf_exempt
def accsmtp_balance(request):
    details = Accsmtp.objects.get(id=1)
    
    url = f"https://accsmtp.com/api/GetBalance.php?username={details.username}&password={details.password}"

    payload={}
    headers = {}
    
    response = requests.request("GET", url, headers=headers, data=payload)
    
    # data = response.json()
    
    print(response.text)
    
    bal = response.text
    
    details.balance = bal
    details.save()
    
    # context = {
    #     "bal": bal,
    # }
    context = {
        "list": bal,
        "the": bal,
        "bal": bal,
        "message": bal,
    }
    return JsonResponse(context)
    
def delete_api_account(request):
    logs = Logs.objects.filter(from_acc=True)
    
    logs.delete()
    
    context = {
        "list": "Done"
    }
    return JsonResponse(context)
    
def backend_index(request):
    if request.user.is_authenticated:
        if request.user.email in ["opemummy466@gmail.com", "teniolamail@gmail.com"]:
            users = User.objects.all().count()
            sales = Order.objects.all().count()
            recent = Order.objects.all().order_by('-date')[:10]
            spent = Order.objects.all().aggregate(Sum('amount'))['amount__sum']
            rate = DollarRate.objects.get(id=1)
            api = Shopviaclone22.objects.get(id=1)
            acc = Accsmtp.objects.get(id=1)
            
            if spent == None:
                bal = "0"
            else:
                bal = spent
        else:
            return redirect("new")
    else:
        return redirect("login")
        
    context = {
            "users": users,
            "sales": sales,
            "recent": recent,
            "spent": bal,
            "rate": rate,
            "api": api,
            "acc": acc,
    }
    return render(request, "core/backend-index.html", context)
    
def backend_orders(request):
    if request.user.is_authenticated:
        if request.user.email in ["opemummy466@gmail.com", "teniolamail@gmail.com"]:
            users = User.objects.all().count()
            sales = Order.objects.all().count()
            recent = Order.objects.all().order_by('-date')
            spent = Order.objects.all().aggregate(Sum('amount'))['amount__sum']
            rate = DollarRate.objects.get(id=1)
            api = Shopviaclone22.objects.get(id=1)
            
            if spent == None:
                bal = "0"
            else:
                bal = spent
        else:
            return redirect("new")
    else:
        return redirect("login")
        
    context = {
            "users": users,
            "sales": sales,
            "recent": recent,
            "spent": bal,
            "rate": rate,
            "api": api,
    }
    return render(request, "core/backend-orders.html", context)
    
def backend_logs(request):
    if request.user.is_authenticated:
        if request.user.email in ["opemummy466@gmail.com", "teniolamail@gmail.com"]:
            users = User.objects.all().count()
            sales = Order.objects.all().count()
            recent = Logs.objects.all().order_by("-id")
            spent = Order.objects.all().aggregate(Sum('amount'))['amount__sum']
            rate = DollarRate.objects.get(id=1)
            api = Shopviaclone22.objects.get(id=1)
            
            if spent == None:
                bal = "0"
            else:
                bal = spent
        else:
            return redirect("new")
    else:
        return redirect("login")
        
    context = {
            "users": users,
            "sales": sales,
            "logs": recent,
            "spent": bal,
            "rate": rate,
            "api": api,
    }
    return render(request, "core/backend-logs.html", context)
    
def backend_category(request):
    if request.user.is_authenticated:
        if request.user.email in ["opemummy466@gmail.com", "teniolamail@gmail.com"]:
            users = User.objects.all().count()
            sales = Order.objects.all().count()
            recent = Category.objects.all().order_by("-id")
            spent = Order.objects.all().aggregate(Sum('amount'))['amount__sum']
            rate = DollarRate.objects.get(id=1)
            api = Shopviaclone22.objects.get(id=1)
            
            if spent == None:
                bal = "0"
            else:
                bal = spent
        else:
            return redirect("new")
    else:
        return redirect("login")
        
    context = {
            "users": users,
            "sales": sales,
            "category": recent,
            "spent": bal,
            "rate": rate,
            "api": api,
    }
    return render(request, "core/backend-category.html", context)
    
def backend_wallet(request):
    if request.user.is_authenticated:
        if request.user.email in ["opemummy466@gmail.com", "teniolamail@gmail.com"]:
            users = User.objects.all().count()
            sales = Order.objects.all().count()
            recent = Wallet.objects.all()
            spent = Order.objects.all().aggregate(Sum('amount'))['amount__sum']
            rate = DollarRate.objects.get(id=1)
            api = Shopviaclone22.objects.get(id=1)
            
            if spent == None:
                bal = "0"
            else:
                bal = spent
        else:
            return redirect("new")
    else:
        return redirect("login")
        
    context = {
            "users": users,
            "sales": sales,
            "wallet": recent,
            "spent": bal,
            "rate": rate,
            "api": api,
    }
    return render(request, "core/backend-wallet.html", context)
    
def backend_users(request):
    if request.user.is_authenticated:
        if request.user.email in ["opemummy466@gmail.com", "teniolamail@gmail.com"]:
            users = User.objects.all()
            sales = Order.objects.all().count()
            recent = Order.objects.all().order_by('-date')
            spent = Order.objects.all().aggregate(Sum('amount'))['amount__sum']
            rate = DollarRate.objects.get(id=1)
            api = Shopviaclone22.objects.get(id=1)
            
            if spent == None:
                bal = "0"
            else:
                bal = spent
        else:
            return redirect("new")
    else:
        return redirect("login")
        
    context = {
        "users": users,
        "sales": sales,
        "recent": recent,
        "spent": bal,
        "rate": rate,
        "api": api,
    }
    return render(request, "core/backend-users.html", context)
    
def view_backend_order(request, id):
    if request.user.is_authenticated:
        if request.user.email in ["opemummy466@gmail.com", "teniolamail@gmail.com"]:
            theorder = Order.objects.get(id=id)
        else:
            return redirect("new")
    else:
        return redirect("login")
        
    context = {
        "u": theorder,
    }
    return render(request, "core/view-backend-order.html", context)
    
def view_backend_category(request, id):
    if request.user.is_authenticated:
        if request.user.email in ["opemummy466@gmail.com", "teniolamail@gmail.com"]:
            theorder = Category.objects.get(id=id)
            
            if request.method == "POST":
                name = request.POST.get('name')
                
                theorder.name = name
                theorder.save()
                
                return redirect("backend-category")
        else:
            return redirect("new")
    else:
        return redirect("login")
        
    context = {
        "u": theorder,
    }
    return render(request, "core/view-backend-category.html", context)
    
def delete_category(request, id):
    if request.user.is_authenticated:
        if request.user.email in ["opemummy466@gmail.com", "teniolamail@gmail.com"]:
            theorder = Category.objects.get(id=id)
            
            theorder.delete()
            
            return redirect("backend-category")
        else:
            return redirect("new")
    else:
        return redirect("login")
        
def delete_log(request, id):
    if request.user.is_authenticated:
        if request.user.email in ["opemummy466@gmail.com", "teniolamail@gmail.com"]:
            theorder = Logs.objects.get(id=id)
            
            theorder.delete()
            
            return redirect("backend-logs")
        else:
            return redirect("new")
    else:
        return redirect("login")

    
def create_backend_category(request):
    if request.user.is_authenticated:
        if request.user.email in ["opemummy466@gmail.com", "teniolamail@gmail.com"]:
            
            if request.method == "POST":
                name = request.POST.get('name')
                
                create_it = Category.objects.create(
                    name=name,
                )
                
                return redirect("backend-category")
        else:
            return redirect("new")
    else:
        return redirect("login")
        
    return render(request, "core/create-new-category-backend.html")
    
def view_backend_logs(request, id):
    if request.user.is_authenticated:
        if request.user.email in ["opemummy466@gmail.com", "teniolamail@gmail.com"]:
            theorder = Logs.objects.get(id=id)
            cat = Category.objects.all()
            
            if request.method == "POST":
                name = request.POST.get('name')
                qty = request.POST.get('qty')
                price = request.POST.get('price')
                description = request.POST.get('description')
                
                options = request.POST.get('options')
                
                thecat = Category.objects.get(id=options)
                
                theorder.name = name
                theorder.qty = qty
                theorder.price = price
                theorder.description = description
                theorder.cat = thecat
                theorder.save()
                
                return redirect("backend-logs")
        else:
            return redirect("new")
    else:
        return redirect("login")
        
    context = {
        "u": theorder,
        "cat": cat,
    }
    return render(request, "core/view-backend-logs.html", context)
    
def create_backend_logs(request):
    if request.user.is_authenticated:
        if request.user.email in ["opemummy466@gmail.com", "teniolamail@gmail.com"]:
            cat = Category.objects.all()
            
            if request.method == "POST":
                name = request.POST.get('name')
                qty = request.POST.get('qty')
                price = request.POST.get('price')
                description = request.POST.get('description')
                
                options = request.POST.get('options')
                
                thecat = Category.objects.get(id=options)
                
                create_it = Logs.objects.create(
                    name=name,
                    qty=qty,
                    price=price,
                    description=description,
                    cat=thecat,
                )
                
                return redirect("backend-logs")
        else:
            return redirect("new")
    else:
        return redirect("login")
        
    context = {
        "cat": cat,
    }
    return render(request, "core/create-new-log-backend.html", context)
    
def view_backend_wallet(request, id):
    if request.user.is_authenticated:
        if request.user.email in ["opemummy466@gmail.com", "teniolamail@gmail.com"]:
            theorder = Wallet.objects.get(id=id)
            
            if request.method == "POST":
                balance = request.POST.get('balance')
                
                theorder.balance = balance
                theorder.save()
                
                return redirect("backend-wallet")
        else:
            return redirect("new")
    else:
        return redirect("login")
        
    context = {
        "u": theorder,
    }
    return render(request, "core/view-backend-wallet.html", context)
 
@csrf_exempt   
def new_accsmtp_account_list(request):
    logs = Logs.objects.filter(from_acc=True)
    delete_cat = Category.objects.filter(from_acc=True)

    details = Accsmtp.objects.get(id=1)
    dollar = DollarRate.objects.get(id=1)
    rate = dollar.rate
    username = details.username
    passw = details.password
    percentage = float(details.percentage)

    url = f"https://accsmtp.com/api/ListResource.php?username={username}&password={passw}"
    response = requests.get(url)
    res = response.text.replace("\n", "").replace("\\n", "")
    data = response.json()

    categories = data.get("categories", [])

    # Clear old data
    logs.delete()
    delete_cat.delete()

    # Prepare for bulk creation
    categories_to_create = []
    logs_to_create = []
    category_id_to_data = {}

    # Filter categories and prepare for creation
    for category in categories:
        category_id = category.get("id")
        if category_id in ["11", "14", "26", "27", "53"]:
            continue

        category_instance = Category(
            name=category.get("name", "Unknown Category"),
            image=category.get("image", "https://logsplace.com/shopviaclone22.com/assets/storage/images/logo_dark_BUP.png"),
            from_acc=True,
        )
        categories_to_create.append(category_instance)
        category_id_to_data[category_id] = {
            "category_data": category,
            "category_obj": category_instance
        }

    # ðŸ”„ Bulk create all categories
    Category.objects.bulk_create(categories_to_create)

    # Now refresh from DB to ensure primary keys are assigned
    saved_categories = Category.objects.filter(from_acc=True)
    name_to_category = {cat.name: cat for cat in saved_categories}

    # Process logs and assign proper category foreign key
    for cat_data in category_id_to_data.values():
        category_obj = name_to_category.get(cat_data["category_obj"].name)
        category_raw_data = cat_data["category_data"]
        accounts = category_raw_data.get("accounts", [])

        for account in accounts:
            account_name = account.get("name", "Unknown Account")
            account_price = account.get("price", "0")
            account_description = account.get("description", "No Description")
            account_id = account.get("id", "")
            account_amount = account.get("amount", "0")
            account_country = account.get("country", "")

            # try:
            convert = float(account_price) / 23000
            naira = convert * float(rate)
            adde = naira + percentage
            final_price = round(adde)
            

            log = Logs(
                name=account_name,
                cat=category_obj,
                from_acc=True,
                api_id=account_id,
                country=account_country,
                qty=account_amount,
                price=final_price,
            )
            logs_to_create.append(log)

    # ðŸ”„ Bulk create all logs
    Logs.objects.bulk_create(logs_to_create)

    context = {
        "list": data,
        "message": "Update Successfully",
        "status": "success",
    }
    return JsonResponse(context)
    
@csrf_exempt    
def clone_shop_api_account_list(request):
    logs = Logs.objects.filter(from_acc=True)
    delete_cat = Category.objects.filter(from_acc=True)
    
    logs.delete()
    delete_cat.delete()
    details = Clonevn.objects.last()
    dollar = DollarRate.objects.get(id=2)
    rate = dollar.rate
    username = details.username
    passw = details.password
    tty = details.percentage
    percentage = float(tty)
            
    url = f"https://shopclone.vn/api/products.php?api_key={details.username}"
    
    payload={}
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    
    response = requests.request("GET", url, headers=headers, data=payload)
    
    res = response.text
    
    data = response.json()


    categories = data.get("categories", [])
    for category in categories:
        category_name = category.get("name", "Unknown Category")
        category_id = category.get("id", "Unknown Category")
        category_icon = category.get("icon", "https://logshubsocials.com/shopviaclone22.com/assets/storage/images/logo_dark_BUP.png")
        # print(f"Category: {category_name}")
        # print(f"    ID: {category_id}")
        
        # if category_id == "77":
        #     continue
        
        skip_categories = [
            "190", "189", "188", "187", "184", "183", "180", "178", "176",
            "172", "171", "170", "166", "158", "157", "103", "102", "97",
            "96", "94", "93", "92", "91", "90", "87", "72", "71", "69", "68",
            "59", "56"
        ]
        
        if category_id in skip_categories:
            continue
        
        create_cat = Category.objects.create(
            name=category_name,
            from_acc=True,
            image=category_icon,
            cat_id=category_id,
        )
    
        accounts = category.get("products", [])
        for account in accounts:
            account_name = account.get("name", "Unknown Account")
            account_price = account.get("price", "Unknown Price")
            dollar_price = float(account_price) * float(0.000038)
            naira_price = float(dollar_price) * float(rate)
            increase = (percentage / 100) * naira_price
            new_value = naira_price + increase
            account_description = account.get("description", "No Description")
            account_id = account.get("id", "No Description")
            account_amount = account.get("amount", "No Description")
            account_country = account.get("country", "No Description")
            # print(f"  Account: {account_name}")
            # print(f"    Price: {naira_price}")
            # print(f"    Description: {account_description}")
            # print(f"    ID: {account_id}")
            # print(f"    Amount: {account_amount}")
            # print(f"    Country: {account_country}")
            # print("-" * 50)
            
            create_log = Logs.objects.create(
                name=account_name,
                description=account_description,
                cat=create_cat,
                from_acc=True,
                api_id=account_id,
                country=account_country,
                qty=account_amount,
                price=new_value,
            )
            
            # delete_vpn = Category.objects.get(cat_id=9)
            # delete_vpn.delete()

    
    # print(response.text)
    
    context = {
        "list": res,
        "message": "Update Successfully",
        "status": "success",
    }
    return JsonResponse(context)
    
@csrf_exempt
def clone_shop_provider_update(request):
    change = Clonevn.objects.last()
    ex = DollarRate.objects.last()
    
    per = request.POST.get("per")
    rate = request.POST.get("rate")
    
    change.percentage = per
    change.save()
    ex.rate = rate
    ex.save()
    
    context = {
        "message": "Update Successfully",
        "status": "success",
    }
    return JsonResponse(context)
    
@csrf_exempt    
def clone_shop_api_balance(request, id):
    details = Clonevn.objects.last()
    # url = f"https://shopclone.vn/api/profile.php?api_key={details.usjername}"
    
    url = f"https://shopclone.vn/api/profile.php?api_key={details.username}"

    payload={}
    headers = {}
    
    response = requests.request("GET", url, headers=headers, data=payload)
    
    data = response.json()
    
    mone = data["data"]["money"]

    money = mone
    
    print(money)
    
    details.balance = money
    details.save()
    
    context = {
        "list": money,
        "the": money,
        "bal": money,
        "message": money,
    }
    return JsonResponse(context)
    
@csrf_exempt
def clone_shop_provider_edit(request):
    current = Clonevn.objects.last()
    drate = DollarRate.objects.last()
    
    context = {
        "api": current,
        "d": drate,
    }
    return render(request, "backend/clone-shop-edit-provider.html", context)
    
@login_required    
def smm_index(request):
        category = SMMCategory.objects.filter(active=True).order_by("-name")
        dspent = SMMOrder.objects.filter(user=request.user).aggregate(Sum('price'))['price__sum'] or 0
        total = SMMOrder.objects.all().count()
        balance = Wallet.objects.get(user=request.user).balance
        
        context = {
            "c": category,
            "spent": dspent,
            "total": total,
            "balance": balance,
        }
        return render(request, "smm/index.html", context)
        
def get_services(request, id):
    # id = request.GET["id"]
    
    cat = SMMCategory.objects.get(id=id)
    ser = SMMService.objects.filter(category=cat)
    
    context = {
        "ser": ser,
    }
    return render(request, "smm/get_services.html", context)
    
def bova_cat(request):
    id = request.GET.get("platformProviders").lower()
    check = SMMCategory.objects.filter(name__icontains=id)
    if check:
        ke = SMMCategory.objects.filter(name__icontains=id).first()
        key = ke.id
    else:
        key = 0
    
    context = {
        "check": check,
        "id": id,
        "key": key,
    }
    return render(request, "smm/bova-cat.html", context)
    
def bova_ser(request):
    id = request.GET.get("platformProviders", 0)
    # id = 6852
    
    scheck = SMMCategory.objects.filter(id=id)
    if scheck:
        check = SMMCategory.objects.get(id=id)
        ser = SMMService.objects.filter(category=check)
    else:
        check = 0
        ser = 0
    
    context = {
        "check": check,
        "ser": ser,
        "id": id,
    }
    return render(request, "smm/bova-ser.html", context)
    
def bova_details(request):
    id = request.GET.get("id_service", 0)
    sser = SMMService.objects.filter(id=id)
    if sser:
        ser = SMMService.objects.get(id=id)
    else:
        ser = 0
    
    context = {
        "ser": ser,
        "id": id,
    }
    return render(request, "smm/bova-details.html", context)
    
@login_required
def smm_order(request):
    
    status = request.GET.get("status")
    
    if not status:
        order = SMMOrder.objects.filter(user=request.user).order_by("-id")
    else:
        if status == "all":
            order = SMMOrder.objects.all().order_by("-id")
        elif status == "processing":
            order = SMMOrder.objects.filter(status="Processing", user=request.user).order_by("-id")
        elif status == "inprogress":
            order = SMMOrder.objects.filter(status="In Progress", user=request.user).order_by("-id")
        elif status == "pending":
            order = SMMOrder.objects.filter(status="Pending", user=request.user).order_by("-id")
        elif status == "completed":
            order = SMMOrder.objects.filter(status="Completed", user=request.user).order_by("-id")
        elif status == "partial":
            order = SMMOrder.objects.filter(status="Partial", user=request.user).order_by("-id")
        elif status == "canceled":
            order = SMMOrder.objects.filter(status="Canceled", user=request.user).order_by("-id")
    
    context = {
        "ser": order,
    }
    return render(request, "smm/orders.html", context)
        
@csrf_exempt
def smm_service_list(request, id):
    SMMCategory.objects.all().delete()
    SMMService.objects.all().delete()
    # perc = request.POST.get("price_percentage_increase")
    perc = 60
    apll = APIs.objects.filter(id=id).update(percentage=perc)
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return redirect("signin")

    # Check if user has superuser status
    if not request.user.is_superuser:
        return redirect("new_order")

    try:
        # Fetch API details
        api = APIs.objects.get(id=id)

        # Fetch dollar rate and percentage
        dollar_rate = DollarRate.objects.get(id=1).rate
        c_api = APIs.objects.filter(status=True).first()

        if not c_api:
            return JsonResponse({"message": "No active API found"}, status=400)

        conversion_factor = float(dollar_rate) * (1 + float(perc) / 100)
        # conversion_factor = float(perc)

        # API Call
        url = f"{api.api_url}?key={api.api_key}&action=services"
        response = requests.post(url)
        the = response.json()

        if not isinstance(the, list):  # Ensure we got a list response
            return JsonResponse({"error": "Invalid API response"}, status=400)

        # Organize categories
        categories = defaultdict(list)
        for item in the:
            categories[item['category']].append(item)

        with transaction.atomic():  # Ensures everything happens faster as a batch
            # Fetch existing categories to avoid unnecessary creation
            existing_categories = {cat.name: cat for cat in SMMCategory.objects.all()}

            # Create new categories in bulk
            new_categories = [
                SMMCategory(name=category_name) for category_name in categories.keys()
                if category_name not in existing_categories
            ]
            if new_categories:
                SMMCategory.objects.bulk_create(new_categories)
                existing_categories.update(
                    {cat.name: cat for cat in SMMCategory.objects.filter(name__in=categories.keys())}
                )

            # Prepare service data for bulk insertion
            services_to_create = []
            services_to_update = []
            existing_services = {s.service_id: s for s in SMMService.objects.all()}

            for category, items in categories.items():
                for item in items:
                    new_naira_price = float(item['rate']) * conversion_factor
                    service_id = item['service']
                    safe_name = item['name']
                    # safe_name = item['name'].encode('ascii', errors='replace').decode('ascii')

                    if service_id in existing_services:
                        # Update existing service
                        existing_service = existing_services[service_id]
                        existing_service.name = safe_name
                        existing_service.type = item['type']
                        existing_service.rate = new_naira_price
                        existing_service.min = item['min']
                        existing_service.max = item['max']
                        existing_service.dripfeed = item['dripfeed']
                        existing_service.refill = item['refill']
                        existing_service.cancel = item['cancel']
                        existing_service.category = existing_categories[category]
                        existing_service.from_id = api.id
                        services_to_update.append(existing_service)
                    else:
                        # Create new service
                        services_to_create.append(
                            SMMService(
                                service_id=service_id,
                                name=safe_name,
                                type=item['type'],
                                rate=new_naira_price,
                                min=item['min'],
                                max=item['max'],
                                dripfeed=item['dripfeed'],
                                refill=item['refill'],
                                cancel=item['cancel'],
                                category=existing_categories[category],
                                from_id=api.id,
                            )
                        )

            # Bulk insert new services
            if services_to_create:
                SMMService.objects.bulk_create(services_to_create, ignore_conflicts=True)

            # Bulk update existing services
            if services_to_update:
                SMMService.objects.bulk_update(
                    services_to_update,
                    ['name', 'type', 'rate', 'min', 'max', 'dripfeed', 'refill', 'cancel', 'category']
                )

    except APIs.DoesNotExist:
        return JsonResponse({"error": "API not found"}, status=404)
    except requests.RequestException as e:
        return JsonResponse({"error": f"API request failed: {str(e)}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
        
    return JsonResponse({
        "status": "success",
        "type": "success",
        "message": "Service list updated successfully",
        "notification_type": "place-order"
    }, status=200)
    
@login_required
# @csrf_exempt
def order_placed(request):
    cat = Category.objects.all()
    ser = Service.objects.all()
    wallet = Wallet.objects.get(user=request.user)
    eorder = Order.objects.all()
    bal = wallet.balance
    order_id = None
    ser_name = None
    dlink = None
    quan = None
    dbal = None
    prompt = None
    
    
    
    if request.method == "POST":
        # category = request.POST.get("category_id")
        service = request.POST.get("service_id")
        link = request.POST.get("singleUrl")
        qty = request.POST.get("singleQuantity")
        
        theser = SMMService.objects.get(id=service)
        it_id = theser.service_id
        
        seprice = theser.rate
        if theser.min == "1":
            ser = float(seprice)
        else:
            ser = float(seprice) / 1000
        tttt = float(ser) * float(qty)
        
        total = tttt
        if float(bal) > float(total):            
            api = APIs.objects.get(status=True)
            
            url = f"{api.api_url}?key={api.api_key}&action=add&service={it_id}&link={link}&quantity={qty}"
            # url = "https://smmtitan.com/api/v2?key=ae714ca3f0d353712333f2252b822881&action=add&service=9579&link=https://tiktok.com&quantity=10"

            response = requests.request("POST", url)
            
            api_res = response.json()
            
            api_order_id = api_res.get("order")
            
            if api_order_id:
                create_order = SMMOrder.objects.create(
                    user=request.user,
                    service=theser,
                    name=theser.name,
                    serviceid=theser.service_id,
                    link=link,
                    qty=qty,
                    price=total,
                    status="Pending",
                    api_key=api.api_key,
                    api_url=api.api_url,
                    api_name=api.name,
                    order_id=api_order_id,
                )
                messages.success(request, "Order Created Successfully")
                
                debit_account = float(bal) - float(total)
                thewallet = Wallet.objects.get(user=request.user)
                thebb = debit_account
                thewallet.balance = thebb
                thewallet.save()
                
                get_bal_again = Wallet.objects.get(user=request.user)
                get_it = get_bal_again.balance
                
                order_id = create_order.id
                ser_name = theser.name
                dlink = link
                quan = qty
                dbal = get_it
                
                prompt = True
            else:
                messages.error(request, "An Error Occured")
        else:
            messages.error(request, "Insufficient Funds")
            api_order_id = 0
            prompt = False
    return redirect("smm_index")
    context = {
        "prompt": prompt,
        "cat": cat,
        "ser": ser,
        "bal": bal,
        "id": api_order_id,
        "ser_name": ser_name,
        "order_id": order_id,
        "dlink": dlink,
        "quan": quan,
        "order": eorder,
        "dbal": dbal,
    }
    # return render(request, "core/order-placed.html", context)
