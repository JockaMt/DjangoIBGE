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
        estados_list = Estado.objects.all().order_by('nome')
        paginator = Paginator(estados_list, 10)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'estados': page_obj,
            'pages': paginator.num_pages,
            'page_number': page_obj.number,
            'title': 'Estados'
        }
        #print(context)
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
        municipios_list = Municipio.objects.all().order_by('nome')
        paginator = Paginator(municipios_list, 10)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'municipios': page_obj,
            'pages': paginator.num_pages,
            'page_number': page_obj.number,
            'title': 'Municípios'
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
        distritos_list = Distrito.objects.all().order_by('nome')
        paginator = Paginator(distritos_list, 10)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'distritos': page_obj,
            'pages': paginator.num_pages,
            'page_number': page_obj.number,
            'title': 'Distritos'
        }
        return render(request, 'distritos.html', context)