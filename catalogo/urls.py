from django.urls import path
# from . import views
from .views import home, catalogo, inicio_sesion, registro,cerrar_sesion, editar_producto, eliminar_producto,agregar_producto, no_autorizado, lista_productos
from django.conf.urls.static import static
from tienda_ropa import settings

urlpatterns = [
    path('', home, name='home'),
    path('catalogo/', catalogo, name='catalogo'),
    path('registro/', registro, name='registro'),
    path('login/', inicio_sesion, name='login'),
    path('logout/', cerrar_sesion, name='logout'),
    
    path('productos/agregar/', agregar_producto, name='agregar_producto'),
    path('productos/lista_productos/', lista_productos, name='lista_productos'),
    path('no-autorizado/', no_autorizado, name='no_autorizado'),
    path('productos/editar/<int:producto_id>/', editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:producto_id>/', eliminar_producto, name='eliminar_producto'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
