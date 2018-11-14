from django.shortcuts import render
from json import JSONEncoder
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from web.models import User,Token,Expense,Income
import datetime
import requests
import smtplib

from postmark import PMMail
from django.conf import settings
import random,string,datetime
from .models import Passwordresetcodes
from django.contrib.auth.hashers import make_password
#mailing:
from django.core.mail import send_mail
from postmarker.core import PostmarkClient

# Create your views here.
@csrf_exempt
#Todo; validate data. user and token and amount might be fake
def submit_expense (request):

    """user submit an expense""" 
    #print("We are Here")
    #print("Im in submit_expense")
    #print(request.POST)

    if 'date' not in request.POST:
        date = datetime.datetime.now()

    this_token = request.POST['token']
    this_user = User.objects.filter(token__token=this_token).get()
    Expense.objects.create(user=this_user, amount=request.POST['amount'], text=request.POST['text'], date=date)

    return JsonResponse({
        'status': 'ok'
    }, encoder=JSONEncoder)
@csrf_exempt
def submit_income(request):

    """user submit an expense"""
    #print("We are Here")
    #print("Im in submit_expense")
    #print(request.POST)

    if 'date' not in request.POST:
        date = datetime.datetime.now()

    this_token = request.POST['token']
    this_user = User.objects.filter(token__token=this_token).get()
    Income.objects.create(user=this_user, amount=request.POST['amount'], text=request.POST['text'], date=date)

    return JsonResponse({
        'status': 'ok'
    }, encoder=JSONEncoder)
random_str = lambda N: ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))

def register(request):
    #if request.POST.has_key('requestcode')python2: #form is filled. if not spam, generate code and save in db, wait for email confirmation, return message
    if 'requestcode' in request.POST: #form is filled. if not spam, generate code and save in db, wait for email confirmation, return message
        #is this spam? check reCaptcha
        if not grecaptcha_verify(request): # captcha was not correct
            context = {'message': 'کپچای گوگل درست وارد نشده بود. شاید ربات هستید؟ کد یا کلیک یا تشخیص عکس زیر فرم را درست پر کنید. ببخشید که فرم به شکل اولیه برنگشته!'} #TODO: forgot password
            return render(request, 'register.html', context)

        if User.objects.filter(email = request.POST['email']).exists(): # duplicate email
            context = {'message': 'متاسفانه این ایمیل قبلا استفاده شده است. در صورتی که این ایمیل شما است، از صفحه ورود گزینه فراموشی پسورد رو انتخاب کنین. ببخشید که فرم ذخیره نشده. درست می شه'} #TODO: forgot password
            #TODO: keep the form data
            return render(request, 'register.html', context)

        if not User.objects.filter(username = request.POST['username']).exists(): #if user does not exists
                code = random_str(48)
                now = datetime.datetime.now()
                email = request.POST['email']
                password = make_password(request.POST['password'])
                username = request.POST['username']
                temporarycode = Passwordresetcodes (email = email, time = now, code = code, username=username, password=password)
                temporarycode.save()

                """message = PMMail(api_key = settings.POSTMARK_API_TOKEN,
                                     subject = "فعال سازی اکانت بستون",
                                     sender = "ali@sabetmikonim.com",
                                     to = email,
                                     text_body = "برای فعال سازی ایمیلی تودویر خود روی لینک روبرو کلیک کنید: http://localhost:8000/accounts/register/?email={}&code={}".format(email, code),
                                     tag = "account request")

                message.send()"""

                """postmark = PostmarkClient(server_token='b53711a5-08c2-403b-9739-0e1521cbc14e')
                postmark.emails.send(
                    From='ali@sabetmikonim.com',
                    To=email,
                    Subject="فعال سازی اکانت بستون",
                    HtmlBody="برای فعال سازی ایمیلی تودویر خود روی لینک روبرو کلیک کنید: http://localhost:8000/accounts/register/?email={}&code={}".format(email, code),
                )
                """
                smtplib.SMTP_SSL()
                send_mail(
                    'فعال سازی اکانت بستون',
                    "برای فعال سازی ایمیلی تودویر خود روی لینک روبرو کلیک کنید: {}?email={}&code={}".format(request.build_absulute_url('.acounts/register/'),email, code),
                    'a.khandan75@gmail.com',
                    [email],
                    fail_silently=False,
                )
                context = {'message': 'ایمیلی حاوی لینک فعال سازی اکانت به شما فرستاده شده، لطفا پس از چک کردن ایمیل، روی لینک کلیک کنید.'}
                return render(request, 'login.html', context)
        else:
            context = {'message': 'متاسفانه این نام کاربری قبلا استفاده شده است. از نام کاربری دیگری استفاده کنید. ببخشید که فرم ذخیره نشده. درست می شه'} #TODO: forgot password
            #TODO: keep the form data
            return render(request, 'register.html', context)
    #elif request.GET.has_key('code'): # user clicked on code //  python2
    elif 'code' in request.GET:
        email = request.GET['email']
        code = request.GET['code']
        if Passwordresetcodes.objects.filter(code=code).exists(): #if code is in temporary db, read the data and create the user
            new_temp_user = Passwordresetcodes.objects.get(code=code)

            this_token = random_str(48)
            newuser = User.objects.create(username=new_temp_user.username, password=new_temp_user.password,
                                          email=new_temp_user.email)
            token = Token.objects.create(user=newuser, token= this_token)
            print("*#########")

            Passwordresetcodes.objects.filter(code=code).delete() #delete the temporary activation code from db
            context = {'message': 'اکانت شما فعال شد. لاگین کنید - البته اگر دوست داشتی'}
            return render(request, 'login.html', context)
        else:
            context = {'message': 'این کد فعال سازی معتبر نیست. در صورت نیاز دوباره تلاش کنید'}
            return render(request, 'login.html', context)
    else:
        context = {'message': ''}
        return render(request, 'register.html', context)
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def grecaptcha_verify(request):
    data = request.POST
    captcha_rs = data.get('g-recaptcha-response')
    url = "https://www.google.com/recaptcha/api/siteverify"
    print("$$",type(settings))
    params = {

        'secret': settings.RECAPTCHA_SECRET_KEY,
        'response': captcha_rs,
        'remoteip': get_client_ip(request)
    }
    verify_rs = requests.get(url, params=params, verify=True)
    verify_rs = verify_rs.json()
    return verify_rs.get("success", False)

def index(request):
    context={}
    return render(request,'index.html',context)