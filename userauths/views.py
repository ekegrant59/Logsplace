from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from .models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm, LogDetailsForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
import shortuuid
import requests
import os
from django.contrib.auth.hashers import make_password
from core.models import LogDetails, Wallet
from django.contrib.auth.password_validation import validate_password

def signup(request):
    if request.user.is_authenticated:
        return redirect("marketplace")
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        confirm = request.POST.get('password_confirmation')
        
        check_username = User.objects.filter(username=username).count()
        check_email = User.objects.filter(email=email).count()
        
        recaptcha_response = request.POST.get('g-recaptcha-response')

        data = {
            'secret': '6LcNfWwrAAAAAJ7uUI0yEG4DwEq3S3FLgIO782n5',
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()
        
        if result.get('success'):
            if check_username:
                messages.error(request, "Username already exist in our database")
                context = {
                    "user": False
                }
            else:
                pass
            if check_email:
                messages.error(request, "Email Address already exist in our database")
                context = {
                    "email": False
                }
            else:
                pass
            if password == confirm:
                    create_user = User.objects.create(
                        username=username,
                        email=email,
                        password=make_password(confirm),
                        email_confirmed=True,
                    )
                    
                    create_wallet = Wallet.objects.create(
                        user=create_user,
                        email=email,
                        balance=0,
                    )
                    user = authenticate(request, username=username, password=confirm)
                    
                    return redirect('marketplace')
            else:
                messages.error(request, "Password Does not Match")
        else:
            messages.error(request, "reCAPTCHA not completed")
            context = {
                "password": False
            }
    # form = CreateUserForm()

    # if request.method == 'POST':
    #     form = CreateUserForm(request.POST)
    #     if form.is_valid():
    #         form.save()
    #         user = form.cleaned_data.get('first_name')
    #         email = form.cleaned_data.get('email')

    #         # messages.success(request, user  + '' ' check your inbox for verification')
            
    #         get_user_unique_id = User.objects.get(email=email)
    #         id = get_user_unique_id.unique_id
    #         email_template = render_to_string('partials/confirm-email.html', {'name': user, 'email': email, 'unique': id})

    #         # Brevo API endpoint for sending transactional emails
    #         api_url = "https://api.brevo.com/v3/smtp/email"
            
    #         # Your Brevo API key
    #         api_key = os.environ.get("BREVO_API_KEY", "")
            
    #         # Email data
    #         email_data = {
    #             "sender": {"name": "Logsplace", "email": "Logsplace@gmail.com"},
    #             "to": [{"email": email, "name": user}],
    #             "subject": "Logsplace Email Verification",
    #             "htmlContent": email_template,
    #         }
            
    #         # Headers for authentication and content type
    #         headers = {
    #             "accept": "application/json",
    #             "api-key": api_key,
    #             "content-type": "application/json"
    #         }
            
    #         # Send the email via a POST request
    #         try:
    #             response = requests.post(api_url, json=email_data, headers=headers)
    #             response.raise_for_status()  # Raises an error for bad responses (4xx or 5xx)
    #             print("Email sent successfully:", response.json())
    #         except requests.exceptions.HTTPError as err:
    #             print("Error sending email:", err)


            # email_send = EmailMessage(
            #     'Logsplace Email Verification',
            #     email_template,
            #     reply_to=['Logsplace@gmail.com'],
            #     [email],
            # )
            
            # email_send = EmailMessage(
            #     subject='Logsplace Email Verification',
            #     body=email_template,
            #     to=[email],
            #     reply_to=['Logsplace@gmail.com']
            # )
            
            # email_send = EmailMessage(
            #      'Logsplace Email Verification',
            #      email_template,
            #      'Logsplace@gmail.com',
            #      [email],
            #  )
            
            # MS_Bw6JFF@trial-3vz9dle6onngkj50.mlsender.net

            # email_send.fail_silently=False
            # email_send.content_subtype == "html"
            # email_send.send()

            # return redirect("email-verify")

    # context = {
    #     'form': form
    # }
    # template = loader.get_template('user/signup.html')
    # return HttpResponse(template.render (request))
    return render(request, "user/signup.html")
    
def email_verify(request):
    return render(request, "user/check-email.html")

def verify(request, unique):
    count_it = User.objects.filter(unique_id=unique).count()

    if count_it:
        check_id = User.objects.get(unique_id=unique)
        check_id.email_confirmed = True
        check_id.save()

        context = {
            "bool": True
        }
    else:
        context = {
            "bool": False
        }
    return render(request, "user/email-verified.html", context)

def signin(request):
    if request.user.is_authenticated:
        return redirect("marketplace")
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Success")
            if request.user.email_confirmed == False:
                logout(request)
            else:
                pass
            next_url = request.GET.get('next', 'marketplace')
            return redirect(next_url)

        else:
            messages.error(request, "Email or Password is incorrect")
    context = {}
    template = loader.get_template('user/login.html')
    return HttpResponse(template.render(context, request))
    
def login_ajax(request):
    success = False
    username = request.GET["username"].lower()
    password = request.GET["password"]
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        messages.success(request, "Success")
        success = True
        msg = "Logged in successfully"
    else:
        success = False
        msg = "Login information is incorrect"
        
    context = {
        "correct": success,
        "msg": msg,
    }
    return JsonResponse(context)
    
def signup_ajax(request):
    username = request.GET["username"].lower()
    email = request.GET["email"]
    password = request.GET["password"]
    repassword = request.GET["repassword"]
    users = False
    email_check = False
    
    if username and email and password and repassword:
        check_username = User.objects.filter(username=username).count()
        check_email = User.objects.filter(email=email).count()
        
        if check_username or check_email:
            msg = "User already exists in our database"
            users = False
        else:
            if password == repassword:
                create_user = User.objects.create(
                    username=username,
                    email=email,
                    password=make_password(repassword),
                    email_confirmed=True,
                )
                
                create_wallet = Wallet.objects.create(
                    user=create_user,
                    email=email,
                    balance=0,
                )
                user = authenticate(request, username=username, password=repassword)
                users = True
                email_check = True
                msg = "Account Created Successfully"
            else:
                users = False
                email_check = False
                msg = "Password Mismatch..."
    else:
        msg = "Fill all form..."
        
        # if check_email:
        #     msg = "Email address already exists in our database"
        #     email_check = False
        # else:
        #     pass
        
        # if password == repassword:
        #     create_user = User.objects.create(
        #         username=username,
        #         email=email,
        #         password=make_password(repassword),
        #         email_confirmed=True,  # Ensure this field exists in your model
        #     )
        #     user = True
        #     email_check = True
        #     users = authenticate(request, username=username, password=repassword)
        #     if users:
        #         login(request, users)
        #     else:
        #         msg = "Account created, but login failed"
        # else:
        #     msg = "Password mismatch, please try again"
    
    context = {
        "user": users,
        "email": email_check,
        "msg": msg,
    }
    
    return JsonResponse(context)
    
def reset_password(request):
    if request.user.is_authenticated:
        return redirect("new")
    
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        
        check_if_user_exist = User.objects.filter(email=email).count()
        
        if check_if_user_exist:
            token = shortuuid.uuid()
            get_user = User.objects.get(email=email)
            user = get_user.first_name
            themail = get_user.email
            get_user.password_reset_token = token
            get_user.save()
            
            email_template = render_to_string('partials/forget-email.html', {'name': user, 'email': email, 'token': token})
    
            email_send = EmailMessage(
                'Logsplace Password Reset',
                email_template,
                'Logsplace@gmail.com',
                [themail],
            )
    
            email_send.fail_silently=False
            email_send.content_subtype == "html"
            email_send.send()
            
            messages.success(request, "Check Your Email to reset password")
            # return redirect("login")
        else:
            messages.error(request, "Email does not exist in our database")
    return render(request, "user/password_reset_form.html")
    
def create_password(request, token):
    if request.user.is_authenticated:
        return redirect("new")
    check_token = User.objects.filter(password_reset_token=token).count()
    
    if check_token:
        context = {
            "bool": True
        }
        if request.method == 'POST':
            # Check if they are the same password
            password = request.POST.get('password')
            new_password = request.POST.get('con_password')
            if password == new_password:
                context = {
                    "pass": True
                }
                change_password = make_password(new_password)
                get_it = User.objects.get(password_reset_token=token)
                get_it.password = change_password
                get_it.password_reset_token = shortuuid.uuid()
                get_it.save()
                
                messages.error(request, "Password Changed")
                return redirect("login")
            else:
                context = {
                    "pass": False
                }
                messages.error(request, "Password does not match")
    else:
        context = {
                    "bool": False
                }
        messages.error(request, "Link Expired")
        return redirect('reset')
    return render(request, 'user/create-password.html', context)
    
def bulk(request):
    email = "opemummy466@gmail.com"
    if request.user.is_authenticated:
        pass
    else:
        return redirect("new")
    
    current_user = User.objects.get(email=email)
    if request.user.email == current_user.email:
        if request.method == 'POST':
            form = LogDetailsForm(request.POST)
            if form.is_valid():
                log = form.cleaned_data['log']
                details = form.cleaned_data['details']
                
                details_list = details.split('*Next*')
                logdetails_instances = [LogDetails(which_log=log, details=detail.strip()) for detail in details_list if detail.strip()]
                LogDetails.objects.bulk_create(logdetails_instances)
                
                messages.success(request, "Bulk Uploaded Successfully")
                return redirect("bulk_added")
        else:
            form = LogDetailsForm()
    else:
        return redirect("new")
        
    context = {
        "form": form
    }
    return render(request, "user/bulk-upload.html", context)
    
def bulk_added(request):
    return render(request, "user/bulk-added.html")

def signout(request):
    logout(request)
    return redirect("login")


import os
import base64
from datetime import datetime
import zipfile

def backup_sqlite_to_brevo(request):
    # Optional: Secure with a key in the URL
    if request.GET.get("key") != "teniteno1":
        return HttpResponse("Unauthorized", status=401)

    # Paths and variables
    db_path = "/home/noncsuoc/Logsplace/Logsplace/db.sqlite3"
    filename = f"db_backup_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.zip"  # ZIP file name
    
    # Path to save the zip file
    zip_path = f"/home/noncsuoc/Logsplace/Logsplace/{filename}"
    
    # Compress the SQLite DB into a ZIP file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(db_path, os.path.basename(db_path))

    # Brevo API config
    api_url = "https://api.brevo.com/v3/smtp/email"
    api_key = os.environ.get("BREVO_API_KEY", "")
    sender_email = "info@thesuftverify.com"

    # List of recipient emails
    to_emails = [
        {"email": "teniolamail@gmail.com", "name": "Logsplace Developer"},
        {"email": "opemummy466@gmail.com", "name": "Logsplace Owner"}
    ]

    try:
        # Read and base64-encode the ZIP file
        with open(zip_path, "rb") as f:
            encoded_db = base64.b64encode(f.read()).decode()

        # Email content with correct attachment structure
        email_data = {
            "sender": {"name": "Logsplace", "email": sender_email},
            "to": to_emails,  # Send to multiple recipients
            "subject": "Logsplace Weekly SQLite DB Backup",
            "htmlContent": "<p>Attached is your Logsplace weekly SQLite DB backup.</p>",
            "attachment": [
                {
                    "content": encoded_db,
                    "name": filename,
                    "type": "application/zip"  # MIME type for ZIP file
                }
            ]
        }

        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }

        # Send the email request
        response = requests.post(api_url, json=email_data, headers=headers)
        
        # Check for successful response
        response.raise_for_status()
        
        # Log and return success
        print(response.json())  # Log the response for debugging
        return HttpResponse("Backup sent successfully.")

    except requests.exceptions.RequestException as err:
        # Log the error response for debugging
        print(err.response.json())
        return HttpResponse(f"Error sending email: {err}")
    except Exception as e:
        return HttpResponse(f"Unexpected error: {e}")
