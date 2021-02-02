from django.shortcuts import render, redirect
from .forms import ApiKeyForm
from setup_apikey.models import APIKEY
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model




# Create your views here.
@login_required(login_url='/login')
def apikey_list(request,id=0):
    
    context = {'apikey_list' : APIKEY.objects.all()}
    return render(request,"api_register/api_list.html", context)

    

@login_required(login_url='/login')
def apikey_form(request,id=0):
    if request.method == "GET":
        if id == 0:
            form = ApiKeyForm()
            print("formget if")
        else:
            apikeyform = APIKEY.objects.get(pk=id)   
            form = ApiKeyForm(instance = apikeyform)
            print("formget else")


        #this below 4 lines capture username and add it to dictionary of context
        
        context = {"form":form}
        return render(request,"api_register/api_form.html", context )
    else:
        if id == 0:
            form = ApiKeyForm(request.POST)
            print("formsavedfindif")
        else:
            apikeyform = APIKEY.objects.get(pk=id)
            form = ApiKeyForm(request.POST, apikeyform)
            print("formsavedfindelse")


        if form.is_valid():
            form.save()
            print("formsaved")
        else:
            print("form not saved")
        
        return redirect('/addapiuser/list')

    
@login_required(login_url='/login')
def apikey_delete(request,id):
    apikeyform = APIKEY.objects.get(pk=id)
    apikeyform.delete()
    return redirect('/addapiuser/list')





