from django.shortcuts import redirect, render,HttpResponse


# Create your views here.
def homePage(request):
    try:
        return render(request, 'home.html', {})
    except Exception as e:
        print(e)
        return HttpResponse("<h1>something went wrong!!!</h1>")    
def aboutUs(request):
    try:
        return render(request, 'about.html', {})
    except Exception as e:
        print(e)
        return HttpResponse("<h1>something went wrong!!!</h1>")       