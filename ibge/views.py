from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from .services import MunicipioImportService, DistritoImportService, EstadoImportService
import logging
import time
from ibge.models import Estado, Municipio, Distrito


logger = logging.getLogger(__name__)


def home(request):
    """View para exibir dados paginados"""
    context = {
        'title': 'Home',
    }
    return render(request, 'index.html', context)


def estados_view(request):
    """View para importação de estados"""
    
    if request.method == 'POST':
        start_time = time.time()
        
        try:
            service = EstadoImportService()
            result = service.import_estados()
            
            elapsed_time = time.time() - start_time
            
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': f"Estados importados com sucesso em {elapsed_time:.2f} segundos",
                    'data': result
                })
            
            messages.success(
                request,
                f"Estados importados com sucesso! {result['created_estados']} estados e "
                f"{result['created_regioes']} regiões criados em {elapsed_time:.2f} segundos"
            )
            
            return redirect('estados')
            
        except Exception as e:
            logger.error(f"Erro na view de estados: {e}")
            
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=500)
            
            messages.error(request, f"Erro na importação: {e}")
            return HttpResponse(f"Erro na importação: {e}", status=500)
    else:
        # Filtragem
        estados_list = Estado.objects.select_related('regiao').all()
        
        # Filtro por região
        regiao_filter = request.GET.get('regiao')
        if regiao_filter:
            estados_list = estados_list.filter(regiao__nome__icontains=regiao_filter)
        
        # Filtro por nome
        nome_filter = request.GET.get('nome')
        if nome_filter:
            estados_list = estados_list.filter(nome__icontains=nome_filter)
        
        # Filtro por sigla
        sigla_filter = request.GET.get('sigla')
        if sigla_filter:
            estados_list = estados_list.filter(sigla__icontains=sigla_filter)
        
        estados_list = estados_list.order_by('nome')
        
        # Paginação
        paginator = Paginator(estados_list, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'estados': page_obj,
            'paginator': paginator,
            'page_obj': page_obj,
            'title': 'Estados',
            'filters': {
                'regiao': regiao_filter or '',
                'nome': nome_filter or '',
                'sigla': sigla_filter or ''
            }
        }
        return render(request, 'estados.html', context)


def municipios_view(request):
    """View para importação de municípios"""
    if request.method == 'POST':
        start_time = time.time()
        
        try:
            service = MunicipioImportService()
            result = service.import_municipios()
            
            elapsed_time = time.time() - start_time
            
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': f"Municípios importados com sucesso em {elapsed_time:.2f} segundos",
                    'data': result
                })
            
            messages.success(
                request,
                f"Municípios importados com sucesso! {result['created']} municípios criados em {elapsed_time:.2f} segundos"
            )
            
            return redirect('municipios')
            
        except Exception as e:
            logger.error(f"Erro na view de municípios: {e}")
            
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=500)
            
            messages.error(request, f"Erro na importação: {e}")
            return HttpResponse(f"Erro na importação: {e}", status=500)
    else:
        # Filtragem
        municipios_list = Municipio.objects.select_related(
            'microrregiao__mesorregiao__uf__regiao',
            'regiao_imediata__regiao_intermediaria__uf'
        ).all()
        
        # Filtro por nome
        nome_filter = request.GET.get('nome')
        if nome_filter:
            municipios_list = municipios_list.filter(nome__icontains=nome_filter)
        
        # Filtro por UF
        uf_filter = request.GET.get('uf')
        if uf_filter:
            municipios_list = municipios_list.filter(
                microrregiao__mesorregiao__uf__sigla__icontains=uf_filter
            )
        
        # Filtro por região
        regiao_filter = request.GET.get('regiao')
        if regiao_filter:
            municipios_list = municipios_list.filter(
                microrregiao__mesorregiao__uf__regiao__nome__icontains=regiao_filter
            )
        
        municipios_list = municipios_list.order_by('nome')
        
        # Paginação
        paginator = Paginator(municipios_list, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'municipios': page_obj,
            'paginator': paginator,
            'page_obj': page_obj,
            'title': 'Municípios',
            'filters': {
                'nome': nome_filter or '',
                'uf': uf_filter or '',
                'regiao': regiao_filter or ''
            }
        }
        return render(request, 'municipios.html', context)


def distritos_view(request):
    """View para importação de distritos"""
    if request.method == 'POST':
        start_time = time.time()
        
        try:
            service = DistritoImportService()
            result = service.import_distritos()
            
            elapsed_time = time.time() - start_time
            
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': f"Distritos importados com sucesso em {elapsed_time:.2f} segundos",
                    'data': result
                })
            
            messages.success(
                request,
                f"Distritos importados com sucesso! {result['created']} distritos criados em {elapsed_time:.2f} segundos"
            )
            
            return redirect('distritos')
            
        except Exception as e:
            logger.error(f"Erro na view de distritos: {e}")
            
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=500)
            
            messages.error(request, f"Erro na importação: {e}")
            return HttpResponse(f"Erro na importação: {e}", status=500)
    else:
        # Filtragem
        distritos_list = Distrito.objects.select_related(
            'municipio',
            'uf',
            'regiao',
            'microrregiao__mesorregiao'
        ).all()
        
        # Filtro por nome
        nome_filter = request.GET.get('nome')
        if nome_filter:
            distritos_list = distritos_list.filter(nome__icontains=nome_filter)
        
        # Filtro por município
        municipio_filter = request.GET.get('municipio')
        if municipio_filter:
            distritos_list = distritos_list.filter(municipio__nome__icontains=municipio_filter)
        
        # Filtro por UF
        uf_filter = request.GET.get('uf')
        if uf_filter:
            distritos_list = distritos_list.filter(uf__sigla__icontains=uf_filter)
        
        # Filtro por região
        regiao_filter = request.GET.get('regiao')
        if regiao_filter:
            distritos_list = distritos_list.filter(regiao__nome__icontains=regiao_filter)
        
        distritos_list = distritos_list.order_by('nome')
        
        # Paginação
        paginator = Paginator(distritos_list, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'distritos': page_obj,
            'paginator': paginator,
            'page_obj': page_obj,
            'title': 'Distritos',
            'filters': {
                'nome': nome_filter or '',
                'municipio': municipio_filter or '',
                'uf': uf_filter or '',
                'regiao': regiao_filter or ''
            }
        }
        return render(request, 'distritos.html', context)