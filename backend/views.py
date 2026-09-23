from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from core.models import Logs, LogDetails, Wallet, Order, Cart, ViewLog, Contact, Transaction_History, Category, LogOrder, Shopviaclone22, DollarRate, Payment, Accsmtp, Bank_Account, ProfileDetails, Clonevn, S2_Num, SMSOrder
from django.db.models import Sum
import uuid
from .models import S2, All
from django.core.files.base import ContentFile
from userauths.models import User
import shortuuid
import requests
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
import json
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files import File
from django.conf import settings
import os
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator

# SMS Section

@csrf_exempt
def s2_balance(request):
    # id = request.GET["id"]
    
    the = S2.objects.last()
    
    url = the.balance_api_url
    
    payload={}
    headers = {}
    
    response = requests.request("GET", url, headers=headers, data=payload)
    
    res = response.text
    
    print(response.text)
    
    if "ACCESS_BALANCE:" in res:
        theb = res.replace("ACCESS_BALANCE:", "").strip()
        # bal = "$" + theb
        bal = theb
        the.balance = bal
        the.save()
    else:
        bal = res
    
    context = {
        "the": res,
        "bal": bal,
        "message": bal,
    }
    return JsonResponse(context)
    
@csrf_exempt
def s2_get_api(request):
    get_current_S2 = S2.objects.filter(status=True).count()
    rate = request.POST.get("dollar_rate")
    rate = 1850
    # perc = request.POST.get("price_percentage_increase")
    perc = 1000
    apll = S2.objects.all().update(percentage=perc)
    dollar_rate = DollarRate.objects.all().last().id
    update_rate = DollarRate.objects.filter(id=dollar_rate).update(rate=rate)
    # upgrade = Upgrade.objects.last()

    if get_current_S2:
        s2_api_details = S2.objects.get(status=True)

        url = s2_api_details.api_url
                               
        payload = {}
        headers = {
            'Authorization': s2_api_details.api_key,
            'Accept': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response.text)

        preview = response.text

        json_data = preview
        data = json.loads(json_data)
        
        price_changed_records = S2_Num.objects.filter(price_changed=True).values('key', 'price')
        
        price_changed_dict = {record['key']: record['price'] for record in price_changed_records}
        
        # Collect all records to be updated in a list
        updated_records = []
        
        # Delete all previous S2_Num entries
        delete_all = S2_Num.objects.all()
        delete_all.delete()

        # Loop through data and collect the records for bulk update
        for identifier, service_data in data['187'].items():
            old_price = price_changed_dict.get(identifier)
            new_price = old_price if old_price is not None else float(service_data['cost'])
            
            naija_rate = float(rate) * float(service_data['cost'])
            
            # naija_rate = float(service_data['cost'])
            
            new_price_add = float(perc) + float(naija_rate)
            
            # vendor_price = (float(upgrade.percentage) / 100 * float(new_price_add))
            
            # new_vendor_price = float(new_price_add) - float(vendor_price)
            custom_price = new_price_add + new_price_add * 35 / 100
            # Create the S2_Num instance
            s2_num_instance = S2_Num(
                key=identifier,
                name=service_data['name'],
                type=service_data['count'],
                price=new_price_add,
                custom_price=custom_price,
                description=service_data['repeatable']
            )
            
            updated_records.append(s2_num_instance)
        
        # Bulk update or create the new records
        if updated_records:
            S2_Num.objects.bulk_create(updated_records)

        context = {
            "pre": preview,
        }

    # Return a success response
    return JsonResponse({
        "status": "success",
        "type": "success",
        "message": "Service list updated successfully",
        "notification_type": "place-order"
    }, status=200)

@csrf_exempt    
def list_all_get_api(request):
    perc = request.POST.get("price_percentage_increase")
    apll = All.objects.all().update(percentage=perc)
    rate = request.POST.get("dollar_rate")
    dollar_rate = DollarRate.objects.all().last().id
    update_rate = DollarRate.objects.filter(id=dollar_rate).update(rate=rate)
    # Return a success response
    return JsonResponse({
        "status": "success",
        "type": "success",
        "message": "Service list updated successfully",
        "notification_type": "place-order"
    }, status=200)
    
@csrf_exempt
def s2_provider_sync(request):
    current = S2.objects.last()
    rate = DollarRate.objects.all().last().rate
    
    context = {
        "api": current,
        "rate": rate,
    }
    return render(request, "backend/sync-provider.html", context)
    
@csrf_exempt
def all_provider_sync(request):
    current = All.objects.last()
    rate = DollarRate.objects.all().last().rate
    
    context = {
        "api": current,
        "rate": rate,
    }
    return render(request, "backend/all-sync-provider.html", context)
    
@csrf_exempt    
def all_balance(request):
    # id = request.GET["id"]
    
    the = All.objects.last()
    
    url = the.balance_api_url
    
    payload={
        "key": the.api_key
    }
    headers = {}
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    res = response.json()
    
    print(response.text)
    
    # bal = "$" + res.get("balance")
    bal = res.get("balance")
    
    the.balance = bal
    the.save()
    
    context = {
        "list": res,
        "real": bal,
        "message": bal,
    }
    return JsonResponse(context)
# LOG Section
    
def index(request):

    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect("bstatistics")
        else:
            return redirect("new")

    if request.method == "POST":
        username = request.POST.get("email")
        password = request.POST.get("password")
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser:
                next_url = request.GET.get('next', 'bstatistics')
                return redirect(next_url)
            else:
                return redirect("new")


    return render(request, "backend/index.html")
    
def statistics(request):
    if not request.user.is_superuser:
        return redirect("new")
    user = User.objects.all()
    new = User.objects.all()[:5]
    wnew = Wallet.objects.all().order_by("-id")[:5]
    order = Order.objects.all()
    dspent = Order.objects.all().aggregate(Sum('amount'))['amount__sum'] or 0
    wall = Wallet.objects.all().aggregate(Sum('balance'))['balance__sum'] or 0
    s2 = Shopviaclone22.objects.all().aggregate(Sum('balance'))['balance__sum'] or 0
    # all = All.objects.all().aggregate(Sum('balance'))['balance__sum'] or 0
    API = float(s2)
    # pending = Order.objects.filter(status="Pending").count()
    # completed = Order.objects.filter(status="Completed").count()
    # processing = Order.objects.filter(status="Processing").count()
    # progress = Order.objects.filter(status="In progress").count()
    # partial = Order.objects.filter(status="Partial").count()
    # canceled = Order.objects.filter(status="Canceled").count()
    # refunded = Order.objects.filter(status="Refunded").count()
    PERCENTAGE_PROFIT = Shopviaclone22.objects.last().percentage
    
    # popular_products = (
    #     Order.objects.values('service')
    #     .annotate(count=Count('id'))
    #     .order_by('-count')[:10]  # ⬅️ Limit to top 10
    # )
    
    # today = timezone.now().date()
    # last_30_days = today - timedelta(days=30)

    # Profit for today
    # daily_profit_qs = (
    #     Order.objects.filter(date__gte=today, status="Completed")
    #     .annotate(
    #         profit=ExpressionWrapper(
    #             F('amount') * PERCENTAGE_PROFIT / 100,  # Dynamically calculate profit percentage
    #             output_field=DecimalField()
    #         )
    #     )
    #     .aggregate(total_profit=Sum('profit'))
    # )
    # daily_profit = daily_profit_qs['total_profit'] or 0

    # Profit for last 30 days
    # monthly_profit_qs = (
    #     Order.objects.filter(date__gte=last_30_days, status="Completed")
    #     .annotate(
    #         profit=ExpressionWrapper(
    #             F('amount') * PERCENTAGE_PROFIT / 100,  # Dynamically calculate profit percentage
    #             output_field=DecimalField()
    #         )
    #     )
    #     .aggregate(total_profit=Sum('profit'))
    # )
    # monthly_profit = monthly_profit_qs['total_profit'] or 0
    
    context = {
        "user": user,
        "order": order,
        "spent": dspent,
        "wall": wall,
        "api": API,
        # "pending": pending,
        # "completed": completed,
        # "processing": processing,
        # "progress": progress,
        # "partial": partial,
        # "canceled": canceled,
        # "refunded": refunded,
        "new": wnew,
        # 'popular_products': popular_products,
        # 'daily_profit': round(daily_profit, 2),
        # 'daily_profit': last_30_days,
        # 'monthly_profit': round(monthly_profit, 2),
    }
        
    return render(request, "backend/statistics.html", context)
    
def orders(request):
    status = request.GET.get("status")
    query = request.GET.get("query", "").lower()
    field = request.GET.get("field")
    page_number = request.GET.get("page", 1)  # get the current page number
    
    # Handle if the user is not authenticated
    if not request.user.is_authenticated:
        return redirect("b_index")
    
    # Handle if the user is not a superuser
    if not request.user.is_superuser:
        return redirect("dashboard")
    
    # Base queryset
    order = Order.objects.all()

    # Handle the search by field
    if field == "id" and query:
        order = order.filter(number_id__icontains=query)
    elif field == "email" and query:
        order = order.filter(user__email__icontains=query)

    # Handle the status filter
    # status_filters = {
    #     "all": Order.objects.all(),
    #     "processing": order.filter(status="Processing"),
    #     "inprogress": order.filter(status="In Progress"),
    #     "pending": order.filter(status="Pending"),
    #     "completed": order.filter(status="Completed"),
    #     "partial": order.filter(status="Partial"),
    #     "canceled": order.filter(status="Canceled"),
    # }

    # if status:
    #     order = status_filters.get(status, order)
    
    order = order.order_by("-id")  # ensure consistent ordering before paginating

    # Apply pagination
    paginator = Paginator(order, 100)  # Show 10 orders per page
    page_obj = paginator.get_page(page_number)

    context = {
        "orders": page_obj,
        "page_obj": page_obj,
    }
    return render(request, "backend/orders.html", context)
    
def sms_orders(request):
    status = request.GET.get("status")
    query = request.GET.get("query", "").lower()
    field = request.GET.get("field")
    page_number = request.GET.get("page", 1)  # get the current page number
    
    # Handle if the user is not authenticated
    if not request.user.is_authenticated:
        return redirect("b_index")
    
    # Handle if the user is not a superuser
    if not request.user.is_superuser:
        return redirect("dashboard")
    
    # Base queryset
    order = SMSOrder.objects.all()

    # Handle the search by field
    if field == "id" and query:
        order = order.filter(number_id__icontains=query)
    elif field == "email" and query:
        order = order.filter(user__email__icontains=query)

    # Handle the status filter
    # status_filters = {
    #     "all": Order.objects.all(),
    #     "processing": order.filter(status="Processing"),
    #     "inprogress": order.filter(status="In Progress"),
    #     "pending": order.filter(status="Pending"),
    #     "completed": order.filter(status="Completed"),
    #     "partial": order.filter(status="Partial"),
    #     "canceled": order.filter(status="Canceled"),
    # }

    # if status:
    #     order = status_filters.get(status, order)
    
    order = order.order_by("-id")  # ensure consistent ordering before paginating

    # Apply pagination
    paginator = Paginator(order, 100)  # Show 10 orders per page
    page_obj = paginator.get_page(page_number)

    context = {
        "orders": page_obj,
        "page_obj": page_obj,
    }
    return render(request, "backend/sms-orders.html", context)
    
def view_orderlog(request, id):
    theorder = Order.objects.get(id=id)
    thelogs = LogOrder.objects.filter(order=theorder)
    
    context = {
        "o": theorder,
        "l": thelogs
    }
    
    return render(request, "backend/view-order.html", context)
    
@csrf_exempt    
def order_bulk_cancel(request):
    if request.method == "POST":
        ids = request.POST.get("ids")
        ids_list = ids.split(",")
        
        Order.objects.filter(id__in=ids_list).delete()
        
    context = {
        "message": "Deleted succesfully",
        "status": "success",
    }
    return JsonResponse(context)
    
def category(request):
    cat = Category.objects.all()
    all = Category.objects.all()
    # dea = Category.objects.filter(active=False)
    # a = Category.objects.filter(active=True)
    
    # Handle the status filter
    status = request.GET.get("status")
    
    if status == "0":
        cat = Category.objects.filter(active=False).order_by("-id")
    elif status == "1":
        cat = Category.objects.filter(active=True).order_by("-id")
    elif status == "2":
        cat = Category.objects.all()
    
    # Base queryset
    query = request.GET.get("query")
    field = request.GET.get("field")
    order = Category.objects.all()

    # Handle the search by field
    # if field == "id" and query:
    #     order = order.filter(order_id__icontains=query)
    if field == "name" and query:
        user = order.filter(name__icontains=query)
    
    context = {
        "cat": cat,
        # "dea": dea,
        # "a": a,
        "all": all,
    }
    return render(request, "backend/category.html", context)
    
@csrf_exempt
def category_new(request):
    return render(request, "backend/new-category.html")
    
@csrf_exempt
def category_update(request, id):
    cat = Category.objects.get(id=id)
    
    # if request.method == "POST":
    #     name = request.POST.get("name")
        
    #     cat.name = name
    #     cat.save()
    
    context = {
        "cat": cat,
    }
    return render(request, "backend/edit-category.html", context)
    
@csrf_exempt
def logdetails_update(request, id):
    cat = LogDetails.objects.get(id=id)
    
    # if request.method == "POST":
    #     name = request.POST.get("name")
        
    #     cat.name = name
    #     cat.save()
    
    context = {
        "cat": cat,
    }
    return render(request, "backend/edit-logdetails.html", context)
    
@csrf_exempt    
def logdetails_edit(request, id):
    cat = LogDetails.objects.get(id=id)
    
    if request.method == "POST":
        name = request.POST.get("details")
        
        cat.details = name
        cat.save()
        
    context = {
        "message": "Update Successfully",
        "status": "success",
    }
    return JsonResponse(context)
    
@csrf_exempt    
def category_delete(request, id):
    order = Category.objects.filter(id=id)
    order.delete()
    
    context = {
        "delete": True,
        "message": "Deleted Successfully",
    }
    return JsonResponse(context)
    
@csrf_exempt    
def logdetails_delete(request, id):
    order = LogDetails.objects.filter(id=id)
    order.delete()
    
    context = {
        "delete": True,
        "message": "Deleted Successfully",
    }
    return JsonResponse(context)
    
# Log Part

@csrf_exempt
def log_update(request, id):
    cat = Logs.objects.get(id=id)
    
    # if request.method == "POST":
    #     name = request.POST.get("name")
        
    #     cat.name = name
    #     cat.save()
    
    context = {
        "cat": cat,
    }
    return render(request, "backend/edit-log.html", context)
    
@csrf_exempt    
def log_edit(request, id):
    cat = Logs.objects.get(id=id)
    
    if request.method == "POST":
        des = request.POST.get("des")
        qty = request.POST.get("qty")
        price = request.POST.get("price")
        
        cat.description = des
        cat.qty = qty
        cat.price = price
        cat.save()
        
    context = {
        "message": "Update Successfully",
        "status": "success",
    }
    return JsonResponse(context)
    
@csrf_exempt    
def log_delete(request, id):
    order = Logs.objects.filter(id=id)
    order.delete()
    
    context = {
        "delete": True,
        "message": "Deleted Successfully",
    }
    return JsonResponse(context)

@csrf_exempt    
def category_edit(request, id):
    cat = Category.objects.get(id=id)
    
    if request.method == "POST":
        name = request.POST.get("name")
        
        cat.name = name
        cat.save()
        
    context = {
        "message": "Update Successfully",
        "status": "success",
    }
    return JsonResponse(context)

@csrf_exempt    
def category_create(request):
    
    if request.method == "POST":
        name = request.POST.get("name")
        
        Category.objects.create(
            name=name
        )
        
    context = {
        "message": "Created Successfully",
        "status": "success",
    }
    return JsonResponse(context)
    
def logs(request):
    if request.user.is_authenticated:
        if request.user.is_superuser == True:
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
            return redirect("index")
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
    
def history(request):
    query = request.GET.get("query", "").lower().strip()
    # query = request.GET.get("query", '').strip()
    field = request.GET.get("field")
    # Get current page number from request
    page_number = request.GET.get("page", 1)  # Default to page 1
    
    if request.user.is_authenticated:
        if request.user.is_superuser == True:
            # Get all transaction history and order by id descending
            his = Transaction_History.objects.all().order_by("-id")
            
            order = Transaction_History.objects.all()

            # Handle the search by field
            if field == "email" and query:
                his = order.filter(user__email__icontains=query).order_by("-id")
            elif field == "transaction_id" and query:
                his = order.filter(id__icontains=query).order_by("-id")

            # Apply pagination
            paginator = Paginator(his, 100)  # Show 100 history entries per page
            page_obj = paginator.get_page(page_number)
        else:
            return redirect("dashboard")
    else:
        return redirect("b_index")
    
    context = {
        "his": page_obj,  # Pass the paginated history to the template
        "page_obj": page_obj,  # Optional, useful for pagination controls in template
    }
    return render(request, "backend/history.html", context)
    
def log(request):
    query = request.GET.get("query", "").lower().strip()
    # query = request.GET.get("query", '').strip()
    field = request.GET.get("field")
    # Get current page number from request
    page_number = request.GET.get("page", 1)  # Default to page 1
    
    if request.user.is_authenticated:
        if request.user.is_superuser == True:
            # Get all transaction history and order by id descending
            his = Logs.objects.all().order_by("-id")
            
            order = Logs.objects.all()

            # Handle the search by field
            if field == "name" and query:
                his = order.filter(name__icontains=query).order_by("-id")
            elif field == "transaction_id" and query:
                his = order.filter(id__icontains=query).order_by("-id")

            # Apply pagination
            paginator = Paginator(his, 100)  # Show 100 history entries per page
            page_obj = paginator.get_page(page_number)
        else:
            return redirect("new")
    else:
        return redirect("b_index")
    
    context = {
        "his": page_obj,  # Pass the paginated history to the template
        "page_obj": page_obj,  # Optional, useful for pagination controls in template
    }
    return render(request, "backend/log.html", context)

    
@csrf_exempt    
def history_delete(request, id):
    order = Transaction_History.objects.filter(id=id).order_by("-id")
    order.delete()
    
    context = {
        "delete": True,
        "message": "Deleted Successfully",
    }
    return JsonResponse(context)
    
def log_details(request):
    if request.user.is_authenticated:
        if request.user.is_superuser == True:
            users = User.objects.all().count()
            sales = Order.objects.all().count()
            recent = LogDetails.objects.all().order_by("-id")
            spent = Order.objects.all().aggregate(Sum('amount'))['amount__sum']
            rate = DollarRate.objects.get(id=1)
            api = Shopviaclone22.objects.get(id=1)
            
            if spent == None:
                bal = "0"
            else:
                bal = spent
        else:
            return redirect("index")
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
    return render(request, "core/backend-logdetails.html", context)
    
# def category(request):
#     if request.user.is_authenticated:
#         if request.user.is_superuser == True:
#             users = User.objects.all().count()
#             sales = Order.objects.all().count()
#             recent = Category.objects.all().order_by("-id")
#             spent = Order.objects.all().aggregate(Sum('amount'))['amount__sum']
#             rate = DollarRate.objects.last()
#             api = Shopviaclone22.objects.get(id=1)
            
#             if spent == None:
#                 bal = "0"
#             else:
#                 bal = spent
#         else:
#             return redirect("index")
#     else:
#         return redirect("login")
        
#     context = {
#             "users": users,
#             "sales": sales,
#             "category": recent,
#             "spent": bal,
#             "rate": rate,
#             "api": api,
#     }
#     return render(request, "core/backend-category.html", context)
    
def wallet(request):
    if request.user.is_authenticated:
        if request.user.is_superuser == True:
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
            return redirect("index")
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
    
def users(request):
    query = request.GET.get("query", "").lower()
    field = request.GET.get("field")
    page_number = request.GET.get("page", 1)

    if request.user.is_authenticated:
        if request.user.is_superuser == True:
            # Base queryset
            user = Wallet.objects.all().order_by("-id")
            order = Wallet.objects.all()

            # Handle the search by field
            if field == "email" and query:
                user = order.filter(user__email__icontains=query).order_by("-id")

            # Apply pagination
            paginator = Paginator(user, 100)  # Show 100 users per page
            page_obj = paginator.get_page(page_number)
        else:
            return redirect("new")
    else:
        return redirect("b_index")

    context = {
        "users": page_obj,
        "page_obj": page_obj,  # Optional, useful for pagination controls
    }
    return render(request, "backend/users.html", context)
    
def logdetails(request):
    query = request.GET.get("query", "").lower()
    field = request.GET.get("field")
    page_number = request.GET.get("page", 1)

    if request.user.is_authenticated:
        if request.user.is_superuser == True:
            # Base queryset
            user = LogDetails.objects.all().order_by("-id")
            order = LogDetails.objects.all()

            # Handle the search by field
            if field == "email" and query:
                user = order.filter(user__email__icontains=query).order_by("-id")

            # Apply pagination
            paginator = Paginator(user, 100)  # Show 100 users per page
            page_obj = paginator.get_page(page_number)
        else:
            return redirect("new")
    else:
        return redirect("b_index")

    context = {
        "users": page_obj,
        "page_obj": page_obj,  # Optional, useful for pagination controls
    }
    return render(request, "backend/logdetails.html", context)
    
@csrf_exempt    
def user_delete(request, id):
    order = User.objects.filter(id=id)
    order.delete()
    
    context = {
        "delete": True,
        "message": "Deleted Successfully",
    }
    return JsonResponse(context)

def add_funds(request, id):
    wallet = Wallet.objects.get(id=id)
    
    context = {
        "user": wallet,
    }
    return render(request, "backend/add-funds.html", context)

@csrf_exempt
def save_funds(request, id):
    wallet = Wallet.objects.get(id=id)
    
    if request.method == "POST":
        amount = request.POST.get("amount")
        old_bal = wallet.balance
        new = float(old_bal) + float(amount)
        wallet.balance = new
        wallet.save()
        
        log_it = Transaction_History.objects.create(
            user=request.user,
            feedback=request.user.email,
            amount=amount,
            status="Approved",
        )
        
    context = {
        "status": "success",
        "type": "success",
        "message": "Funds added successfully",
        "notification_type": "place-order",
    }
    return JsonResponse(context)

@csrf_exempt    
def user_bulk(request):
    if request.method == "POST":
        ids = request.POST.get("ids")
        ids_list = ids.split(",")
        
        User.objects.filter(id__in=ids_list).delete()
        
        # for i in ids_list:
        #     code = i
        #     w = User.objects.filter(id=code)
        #     w.delete()
        
    context = {
        "message": "Deleted succesfully",
        "status": "success",
    }
    return JsonResponse(context)
    
def view_order(request, id):
    if request.user.is_authenticated:
        if request.user.is_superuser == True:
            theorder = Order.objects.get(id=id)
        else:
            return redirect("index")
    else:
        return redirect("login")
        
    context = {
        "u": theorder,
    }
    return render(request, "core/view-backend-order.html", context)
    
def view_category(request, id):
    if request.user.is_authenticated:
        if request.user.is_superuser == True:
            theorder = Category.objects.get(id=id)
            
            if request.method == "POST":
                name = request.POST.get('name')
                
                theorder.name = name
                theorder.save()
                
                return redirect("backend-category")
        else:
            return redirect("index")
    else:
        return redirect("login")
        
    context = {
        "u": theorder,
    }
    return render(request, "core/view-backend-category.html", context)
    
def delete_category(request, id):
    if request.user.is_authenticated:
        if request.user.is_superuser == True:
            theorder = Category.objects.get(id=id)
            
            theorder.delete()
            
            return redirect("backend-category")
        else:
            return redirect("index")
    else:
        return redirect("login")
        
def delete_log(request, id):
    if request.user.is_authenticated:
        if request.user.is_superuser == True:
            theorder = Logs.objects.get(id=id)
            
            theorder.delete()
            
            return redirect("backend-logs")
        else:
            return redirect("index")
    else:
        return redirect("login")
        
def delete_log_details(request, id):
    if request.user.is_authenticated:
        if request.user.is_superuser == True:
            theorder = LogDetails.objects.get(id=id)
            
            theorder.delete()
            
            return redirect("backend-log-details")
        else:
            return redirect("index")
    else:
        return redirect("login")

    
def create_category(request):
    if request.user.is_authenticated:
        if request.user.is_superuser == True:
            
            if request.method == "POST":
                name = request.POST.get('name')
                
                create_it = Category.objects.create(
                    name=name,
                )
                
                return redirect("backend-category")
        else:
            return redirect("index")
    else:
        return redirect("login")
        
    return render(request, "core/create-new-category-backend.html")
    
def view_logs(request, id):
    if request.user.is_authenticated:
        if request.user.is_superuser == True:
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
            return redirect("index")
    else:
        return redirect("login")
        
    context = {
        "u": theorder,
        "cat": cat,
    }
    return render(request, "core/view-backend-logs.html", context)
    
def view_log_details(request, id):
    if request.user.is_authenticated:
        if request.user.is_superuser == True:
            theorder = LogDetails.objects.get(id=id)
            cat = Logs.objects.all()
            
            if request.method == "POST":
                name = request.POST.get('name')
                qty = request.POST.get('qty')
                price = request.POST.get('price')
                description = request.POST.get('description')
                
                options = request.POST.get('options')
                
                thecat = LogDetails.objects.get(id=options)
                
                theorder.details = description
                theorder.which_log = thecat
                theorder.save()
                
                return redirect("backend-log-details")
        else:
            return redirect("index")
    else:
        return redirect("login")
        
    context = {
        "u": theorder,
        "cat": cat,
    }
    return render(request, "core/view-backend-log-details.html", context)
    
def create_logs(request):
    if request.user.is_authenticated:
        if request.user.is_superuser == True:
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
            return redirect("index")
    else:
        return redirect("login")
        
    context = {
        "cat": cat,
    }
    return render(request, "core/create-new-log-backend.html", context)
    
def view_wallet(request, id):
    if request.user.is_authenticated:
        if request.user.is_superuser == True:
            theorder = Wallet.objects.get(id=id)
            
            if request.method == "POST":
                balance = request.POST.get('balance')
                
                theorder.balance = balance
                theorder.save()
                
                return redirect("backend-wallet")
        else:
            return redirect("index")
    else:
        return redirect("login")
        
    context = {
        "u": theorder,
    }
    return render(request, "core/view-backend-wallet.html", context)
    
def bulk(request):
    log = Logs.objects.filter(from_api=False, from_acc=False)
    if request.user.is_authenticated:
        if request.user.is_superuser == True:
            if request.method == 'POST':
                options = request.POST.get("options")
                
                the_log = Logs.objects.get(id=options)
                details = request.POST.get("description")
                
                details_list = details.split('*Next*')
                logdetails_instances = [LogDetails(which_log=the_log, details=detail.strip()) for detail in details_list if detail.strip()]
                LogDetails.objects.bulk_create(logdetails_instances)
                
                messages.success(request, "Bulk Uploaded Successfully")
                # return redirect("backend-logs")
        else:
            return redirect("new")
    else:
        return redirect("b_index")
        
    context = {
        "log": log,
    }
    return render(request, "backend/bulk.html", context)
    
def bulk_profile(request):
    log = Logs.objects.filter(from_api=False, from_acc=False)
    if request.user.is_authenticated:
        if request.user.is_superuser == True:
            if request.method == 'POST':
                options = request.POST.get("options")
                
                the_log = Logs.objects.get(id=options)
                details = request.POST.get("description")
                
                details_list = details.split('*Next*')
                logdetails_instances = [ProfileDetails(which_log=the_log, details=detail.strip()) for detail in details_list if detail.strip()]
                ProfileDetails.objects.bulk_create(logdetails_instances)
                
                messages.success(request, "Bulk Uploaded Successfully")
                # return redirect("backend-logs")
        else:
            return redirect("new")
    else:
        return redirect("b_index")
        
    context = {
        "log": log,
    }
    return render(request, "backend/bulk-profile.html", context)
    
# def delete_manual(request, id):
#     if request.user.is_authenticated:
#         if request.user.is_superuser == True:
#             theorder = Manual_Deposit.objects.get(id=id)
#             theorder.delete()
                
#             return redirect("backend-manual")
#         else:
#             return redirect("index")
#     else:
#         return redirect("login")
    
    
# def view_manual(request, id):
#     if request.user.is_authenticated:
#         if request.user.is_superuser == True:
#             theorder = Manual_Deposit.objects.get(id=id)
            
#             if request.method == "POST":
#                 # amount = request.POST.get('amount')
#                 status = request.POST.get('status')
                
#                 theorder.status = status
#                 theorder.save()
                
#                 # use = theorder.amount
#                 # Update User Balance
                
#                 amount = theorder.amount
#                 duser = theorder.user
#                 wallet = Wallet.objects.get(user=duser)
#                 bal = wallet.balance
#                 add = amount
#                 toge = float(bal) + float(add)
#                 wallet.balance = toge
#                 wallet.save()
                
                
#                 return redirect("backend-manual")
#         else:
#             return redirect("index")
#     else:
#         return redirect("login")
        
#     context = {
#         "u": theorder,
#     }
#     return render(request, "core/view-backend-manual.html", context)

# def manual(request):
#     if request.user.is_authenticated:
#         if request.user.is_superuser == True:
#             users = User.objects.all().count()
#             sales = Order.objects.all().count()
#             recent = Manual_Deposit.objects.filter(status="Pending")
            
#         else:
#             return redirect("index")
#     else:
#         return redirect("login")
        
#     context = {
#             "users": users,
#             "sales": sales,
#             "manual": recent,
#     }
#     return render(request, "core/backend-manual.html", context)
    
def provider(request):
    provider = Shopviaclone22.objects.all()
    p = Clonevn.objects.all()
    s = S2.objects.all()
    a = All.objects.all()
    
    context = {
        "pro": provider,
        "p": p,
        "s": s,
        "a": a,
    }
    return render(request, "backend/provider.html", context)

@csrf_exempt    
def api_balance(request, id):
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
        "the": money,
        "bal": money,
        "message": money,
    }
    return JsonResponse(context)
    
@csrf_exempt
def provider_edit(request):
    current = Shopviaclone22.objects.last()
    drate = DollarRate.objects.last()
    
    context = {
        "api": current,
        "d": drate,
    }
    return render(request, "backend/edit-provider.html", context)
    
@csrf_exempt
def accsprovider_edit(request):
    current = Accsmtp.objects.last()
    drate = DollarRate.objects.last()
    
    context = {
        "api": current,
        "d": drate,
    }
    return render(request, "backend/edit-accs-provider.html", context)
    
@csrf_exempt
def payment(request):
    pay = Payment.objects.all()
    
    context = {
        "pay": pay,
    }
    return render(request, "backend/payment.html", context)

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
        
        create_cat = Category.objects.create(
            name=category_name,
            from_api=True,
            image=category_icon,
        )
    
        accounts = category.get("products", [])
        for account in accounts:
            account_name = account.get("name", "Unknown Account")
            account_price = account.get("price", "Unknown Price")
            naira_price = float(account_price) * float(rate)
            increase = (percentage / 100) * naira_price
            new_val = float(naira_price) + float(percentage)
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
                from_api=True,
                api_id=account_id,
                country=account_country,
                qty=account_amount,
                price=new_val,
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
def provider_update(request):
    change = Shopviaclone22.objects.last()
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
def accsprovider_update(request):
    change = Accsmtp.objects.last()
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
def clone_shop_api_account_list(request):
    # Clean up old cloned data
    Logs.objects.filter(from_acc=True).delete()
    Category.objects.filter(from_acc=True).delete()
    
    # Get clone credentials and conversion rates
    details = Clonevn.objects.last()
    dollar = DollarRate.objects.last()
    rate = dollar.rate
    percentage = float(details.percentage)
    
    
    allowed_category_ids = ["100", "107", "76", "68", "56", "72", "73", "74", "105", "101", "106", "55"]

    # Make request to external API
    url = f"https://shopclone.vn/api/products.php?api_key={details.username}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    try:
        data = response.json()
    except Exception as e:
        return JsonResponse({
            "message": f"Failed to parse JSON: {str(e)}",
            "status": "error"
        }, status=500)
    
    categories = data.get("categories", [])
    
    for category in categories:
        category_id = str(category.get("id", ""))
        
        # ✅ Skip if category ID is not in allowed list
        # if category_id not in allowed_category_ids:
        #     continue
        
        category_name = category.get("name", "Unknown Category")
        category_icon = category.get("icon", "https://logshubsocials.com/shopviaclone22.com/assets/storage/images/logo_dark_BUP.png")
        
        create_cat = Category.objects.create(
            name=category_name,
            from_acc=True,
            image=category_icon,
            cat_id=category_id,
        )
        
        accounts = category.get("products", [])
        for account in accounts:
            account_name = account.get("name", "Unknown Account")
            account_price = float(account.get("price", 0))
            dollar_price = account_price * 0.000038
            naira_price = float(dollar_price) * float(rate)
            increase = (percentage / 100) * naira_price
            final_price = naira_price + increase
            
            Logs.objects.create(
                name=account_name,
                description=account.get("description", ""),
                cat=create_cat,
                from_acc=True,
                api_id=account.get("id", ""),
                country=account.get("country", ""),
                qty=account.get("amount", "0"),
                price=final_price,
            )
    
    return JsonResponse({
        "message": "Update Successfully",
        "status": "success"
    })
    
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
    
def add_new_log(request):
    cat = Category.objects.filter(from_api=False, from_acc=False)
    
    if request.method == "POST":
        name = request.POST.get("log")
        image = request.FILES.get("log_image")
        category = request.POST.get("log_cat")
        description = request.POST.get("description")
        price = request.POST.get("log_price")
        qty = request.POST.get("log_qty")
        
        create_log = Logs.objects.create(
            name=name,
            cat=Category.objects.get(id=category),
            image=image,
            description=description,
            price=price,
            qty=qty,
        )
        
        return redirect("bulk")
    
    context = {
        "c": cat,
    }
    return render(request, "backend/new-log.html", context)
    
def lout(request):
    logout(request)
    return redirect("b_index")