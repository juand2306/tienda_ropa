from django.urls import path
# from . import views
from .views import home, catalogo, inicio_sesion, registro,cerrar_sesion, editar_producto, eliminar_producto,agregar_producto, no_autorizado, lista_productos
from django.conf.urls.static import static
from tienda_ropa import settings
from django.contrib.auth import views as auth_views
from . import views

app_name = 'catalogo'

urlpatterns = [
    # Páginas públicas
    path('', views.home, name='home'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    
    # Autenticación
    path('registro/', views.registro, name='registro'),
    path('login/', views.inicio_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
    
    # Administración de productos
    path('administrador/productos/', views.lista_productos, name='lista_productos'),
    path('administrador/productos/agregar/', views.agregar_producto, name='agregar_producto'),
    path('administrador/productos/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('administrador/productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    
    # Categorías
    path('administrador/categorias/', views.lista_categorias, name='lista_categorias'),
    path('administrador/categorias/agregar/', views.agregar_categoria, name='agregar_categoria'),
    path('administrador/categorias/editar/<int:categoria_id>/', views.editar_categoria, name='editar_categoria'),
    path('administrador/categorias/eliminar/<int:categoria_id>/', views.eliminar_categoria, name='eliminar_categoria'),
    
    # Errores y utilidades
    path('no-autorizado/', views.no_autorizado, name='no_autorizado'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
