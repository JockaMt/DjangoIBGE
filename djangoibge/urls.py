
"""
URL configuration for djangoibge project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from ibge import views as ibge_views
from empresas import views as empresas_views
from django.urls import path, include

urlpatterns = [
    path("__reload__/", include("django_browser_reload.urls")),
    path('', ibge_views.home, name='home'),
    path('estados/', ibge_views.estados_view, name='estados'),
    path('municipios/', ibge_views.municipios_view, name='municipios'),
    path('distritos/', ibge_views.distritos_view, name='distritos'),
    path('empresas/', empresas_views.empresas_view, name='empresas'),
    path('admin/', admin.site.urls),
]
