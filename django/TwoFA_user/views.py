from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import User_twofa
import random
import math
import pyotp
import qrcode
            
            


# Create your views here.


@login_required(login_url='/login')
def twoFADash_index(request):
    if request.method == "GET":
        us = str(request.user)
        context = {'own_name': us}
        # print("two fa index")
        return render(request, 'twoFADash/base.html', context)
    else:
        us = str(request.user.id)
        context = {'own_name': us}
        input_countrycode = request.POST['countryCode']
        input_mobile_number= request.POST['mobile']
        #for key, value in request.session.items():
        	#print('{} => {}'.format(key, value))
       
        context = {'own_name': us,'countrycode': input_countrycode,'mobile_number': input_mobile_number,'session':request.user}

        #user_update_data = User.objects.get(pk=us)
       # if User_twofa.objects.filter(pk = us).exists():

        if User_twofa.objects.filter(pk = us).exists():
            print("row exists")

        else:
            User_twofa_row = User_twofa(pk = us)
            User_twofa_row.save()




        t = User_twofa.objects.get(pk=us)

        t.countrycode = str(input_countrycode)
        t.mobile_number = input_mobile_number

        digits = [i for i in range(0, 10)]
        random_str = ""
      

        for i in range(6):
            index = math.floor(random.random() * 10)
            random_str += str(digits[index])

        t.secret_key_otp = random_str
        t.two_fa_activated = False
        t.save()







        return render(request, 'twoFADash/otp_page.html', context)
    
"""

@login_required(login_url='/login')
def send_message_for_activation(request):
    if request.method == "GET":
        us = str(request.user)
        context = {'own_name': us}
        print("send_message_for_activation--------get")
        return render(request, 'twoFADash/base.html', context)
        

    else:
        us = str(request.user)
        context = {'own_name': us}
        print("send_message_for_activation--------get")
        return render(request, 'twoFADash/base.html', context)



        """

@login_required(login_url='/login')
def twoFAgoogle_index(request):
    if request.method == "GET":
        us = str(request.user.id)
        
        if User_twofa.objects.filter(pk = us).exists():
            print("2fa row exists 92")

        else:
            User_twofa_row = User_twofa(pk = us)
            User_twofa_row.save()

        fetch_User_twofa = User_twofa.objects.get(pk=us)
        two_fa_status = fetch_User_twofa.two_fa_activated
        

        context = {'own_name': us,"status_activate":two_fa_status}




        
        return render(request, 'twoFADash/google2fa.html', context)
    else:
        context = {'own_name': us,}
        return render(request, 'twoFADash/google2fa.html', context)



@login_required(login_url='/login')
def twoFAGActivatePage(request):
    if request.method == "GET":
        us = str(request.user.id)

        #print("two fa index")
        if User_twofa.objects.filter(pk = us).exists():
            print("row exists")

        else:
            User_twofa_row = User_twofa(pk = us)
            User_twofa_row.save()

        fetch_User_twofa = User_twofa.objects.get(pk=us)
        twofa_activ_status = fetch_User_twofa.two_fa_activated
        secretkey_uuid = fetch_User_twofa.secret_key_google
        if twofa_activ_status == False:
            if secretkey_uuid == 'na':
                #got_string = str(base32.generate(length=30))
                #without_zero=got_string.replace('0', '2')
                #without_one=without_zero.replace('1', '5')
                #without_eight =without_one.replace('8', '4')
                #sanitised_secreatekey = without_eight.replace('9', '3')

                fetch_User_twofa.secret_key_google = pyotp.random_base32()
                secreate_key = fetch_User_twofa.secret_key_google
                fetch_User_twofa.save()
                user_name = str(request.user)
                string_qrcode = pyotp.totp.TOTP(secreate_key).provisioning_uri(name= user_name , issuer_name='Trading_Tools')
                qr = qrcode.make(string_qrcode)
                QRimage_path ="content/static/qrcode/"
                image_address= QRimage_path + us + ".png"
                qr.save(image_address)

            else:
                fetch_User_twofa = User_twofa.objects.get(pk=us)
                secreate_key = fetch_User_twofa.secret_key_google


        context = {'own_name': us,'secreate_key': secreate_key,}
        return render(request, 'twoFADash/google2FAQrCodePage.html', context)
    else:
        us = str(request.user.id)
        codenumber=request.POST['authcodenumber']
       # print("inputcodenumber",codenumber)

        fetch_User_twofa = User_twofa.objects.get(pk=us)
        fetched_secreate_key = str(fetch_User_twofa.secret_key_google)
        totp=pyotp.TOTP(fetched_secreate_key)
        verification_status = totp.verify(codenumber)
        if verification_status == True:

            fetch_User_twofa = User_twofa.objects.get(pk=us)
            fetch_User_twofa.two_fa_activated = True
            fetch_User_twofa.save()

            context = {'own_name': us,'verification_status': verification_status,}
            

            return render(request, 'twoFADash/g2FActivationSuccess.html', context)
        else:
            context = {'own_name': us,}
            return render(request, 'twoFADash/g2FActivationFail.html', context)

        
        

