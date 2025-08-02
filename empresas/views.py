from django.shortcuts import render, redirect
from .services import EmpresasService

# Create your views here.
def empresas_view(request):
    """View para exibir a página de empresas"""
    # empresas = EmpresasService()
    # empresas.get_data()
    
    context = {
        'title': 'Empresas',
    }
    return render(request, 'empresas.html', context)  # Redireciona para a página inicial ou outra view conforme necessário