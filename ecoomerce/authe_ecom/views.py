from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
#To Activate user Account 
from django.contrib.sites.shortcuts import get_current_site #to get the current url of site.
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode# for decoding and encoding the strings.
from django.urls import NoReverseMatch,reverse #check the reverse match.
from django.template.loader import render_to_string # to covnvert into strings
from django.utils.encoding import force_bytes,force_str,DjangoUnicodeDecodeError # convert in to some 64byte or 32 bytes
#getting tokes form utils.py
from .utils import TokenGenerator,generate_token
#Emails
from django.core.mail import send_mail,EmailMultiAlternatives#send the mail
from django.core.mail import BadHeaderError #When error occurs we use it.
from django.core import mail 
from django.conf import settings# to give a host mail  data
from django.core.mail import EmailMessage
#threading
import threading
#reset7 passowrd generators
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class EmailThread(threading.Thread):
    def __init__(self,email_message):
        self.email_message=email_message
        threading.Thread.__init__(self)
    def run(self):
        self.email_message.send()


def signin(request):
    if request.method=="POST":
            email=request.POST.get("email")
            password=request.POST.get("pass1")
            conf_password=request.POST.get("pass2")

            if password!=conf_password:
                messages.warning(request,"Password is incorrect")
                return redirect("/auth/signin")

            try:
                if User.objects.get(username=email):
                    messages.warning(request,"Email is Taken")
                    return redirect("/auth/signin")
            except Exception as identifier:
                pass
            
            user=User.objects.create_user(email,email,password)
            user.is_active=False
            user.save()
            current_site=get_current_site(request)
            email_subject="Activate Your Account"
            message=render_to_string("auth/activate.html",{
                'user':user,
                'domain':'127.0.0.1:8000',
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':generate_token.make_token(user)
            })
           
            email_message=EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email],)
            EmailThread(email_message).start()
            messages.info(request,"Activate Your Account by clicking link on your email")
            return redirect("/auth/login")

    return render(request,"auth/signin.html")

class ActivateAccountView(View):
    def get(self,request,uidb64,token):
        try: 
            uid =force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=uid)
        except Exception as identifier:
            user=None
        if user is not None and generate_token.check_token(user,token):
            user.is_active=True
            user.save()
            messages.info(request,"Account activated successfully")
            return redirect("/auth/login")
        return render(request,"auth/activatefail.html")
        
def handlelogin(request):
    if request.method=="POST":
            usern=request.POST.get("email")
            pass1=request.POST.get("pass")
            myuser=authenticate(username=usern,password=pass1)
            
            if myuser is not None:
                login(request,myuser)
                messages.success(request,"login successful")
                return render(request,"index.html")
            else:
                messages.error(request,"login unsuccessful")
                return redirect("/auth/login")

    return render(request,"auth/login.html")



def handlelogout(request):
    login(request)
    messages.success(request,"logout successful")
    return redirect("/auth/login")

class  RequestRestEmailView(View):
    def get(self,request):
        return render(request,'auth/request-reset-email.html') 
    def post(self,request):
        email=request.POST.get("email")
        user=User.objects.filter(email=email)

        if user.exists():
            current_site=get_current_site(request)
            email_subject="[Reset the Password]"
            message=render_to_string("auth/reset-user-pasword.html",{
                'domain':'127.0.0.1:8000',
                'uid':urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0])
            })
            email_message=EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email])
            EmailThread(email_message).start()

            messages.info(request,"WE HAVE SEND YOU A EMAIL ON HOW TO RESET A PASSWORD")
            return render(request,'auth/request-reset-email.html')

class  SetNewpasswordView(View):
    def get(self,request,uidb64,token):
        context={
            'uidb64':uidb64,
            'token':token
        }
        try: 
            user_id =force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user,token):
                messages.warning(request,'Password Reset Link is Invalid')
                return render(request,"auth/request-reset-email.html")
        except DjangoUnicodeDecodeError  as identifier:
            pass
        return render(request,"auth/set-new-password.html",context)
        
    def post(self,request,uidb64,token):
        context={
              'uidb64':uidb64,
               'token':token
        }
        password=request.POST["pass1"]
        conf_password=request.POST["pass2"]

        if password!=conf_password:
            messages.warning(request,'Password not matching')
            return render(request,"auth/set-new-password.html",context)
            
        try:
            user_id =force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset success please login')
            return redirect("/auth/login/")

        except DjangoUnicodeDecodeError  as identifier:
            messages.error(request,"something went wrong")
            return render(request,"auth/set-new-password.html",context)
            
        return render(request,"auth/set-new-password.html",context)


        