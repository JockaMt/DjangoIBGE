from django.shortcuts import redirect

# Create your views here.
def empresas_view(request):
    """View para exibir a página de empresas"""
    context = {
        'title': 'Empresas',
    }
    return redirect('home')  # Redireciona para a página inicial ou outra view conforme necessário