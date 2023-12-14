from django.contrib.auth import login, logout
from django.contrib.auth.views import AuthenticationForm
from django.shortcuts import redirect, render
from .forms import UserRegistrationForm



def user_register(request):
    if request.method == 'POST':
        print("hello")
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('')
        print(form.errors)
        return render(request, 'register.html',{'form': form, 'errors': form.errors})
    else:
        form = UserRegistrationForm()
        context = {'form':form}
        return render(request, 'register.html', context)


def user_login(request):
    context = {}
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('user_receipts')
        context['form'] = form
        context['errors'] = form.errors
    else:
        form = AuthenticationForm()
        context['form'] = form
    return render(request, 'login.html', context)
        

def user_logout(request):
    logout(request)
    return redirect('login')
    

    

