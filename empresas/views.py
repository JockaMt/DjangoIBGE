from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Empresa
from .services import EmpresasService


@login_required
def empresas_view(request):
    """View otimizada para exibir a página de empresas"""
    if request.method == 'POST':
        try:
            EmpresasService.get_data()
            messages.success(request, "Empresas importadas com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro na importação: {e}")
        
        return redirect('empresas')
    
    # Constrói o queryset com filtros ANTES da paginação
    empresas_queryset = Empresa.objects.only(
        'cnpj_basico', 
        'rasao_social', 
        'natureza_juridica', 
        'clasificacao_do_responsavel', 
        'capital_social', 
        'porte', 
        'ente_federativo_responsavel'
    )

    # Aplicar filtros
    rasao_social_filter = request.GET.get('rasao_social')
    if rasao_social_filter:
        empresas_queryset = empresas_queryset.filter(rasao_social__icontains=rasao_social_filter)
    
    cnpj_basico_filter = request.GET.get('cnpj_basico')
    if cnpj_basico_filter:
        empresas_queryset = empresas_queryset.filter(cnpj_basico=cnpj_basico_filter)
    
    porte_filter = request.GET.get('porte')
    if porte_filter:
        empresas_queryset = empresas_queryset.filter(porte=porte_filter)
    
    # Ordenação
    empresas_queryset = empresas_queryset.order_by('rasao_social')

    # Paginação otimizada - só carrega os registros da página atual
    paginator = Paginator(empresas_queryset, 30)
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)

    context = {
        'title': 'Empresas',
        'empresas': page_obj,
        'paginator': paginator,
        'page_obj': page_obj,
        'filters': {
            'rasao_social': rasao_social_filter or '',
            'cnpj_basico': cnpj_basico_filter or '',
            'porte': porte_filter or '',
        }
    }
    return render(request, 'empresas.html', context)