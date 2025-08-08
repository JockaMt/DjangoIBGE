from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

def login(request):
    """View personalizada para login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                auth_login(request, user)
                messages.success(request, f'Bem-vindo, {username}!')
                
                # Redirecionar para a página solicitada ou home
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Usuário ou senha incorretos.')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = AuthenticationForm()
    
    context = {
        'title': 'Login',
        'form': form
    }
    return render(request, 'login.html', context)

def register(request):
    """View para registro de usuário"""
    return render(request, 'login.html')

@login_required
def logout(request):
    """View personalizada para logout"""
    username = request.user.username
    auth_logout(request)
    messages.success(request, f'Até logo, {username}!')
    return redirect('login')