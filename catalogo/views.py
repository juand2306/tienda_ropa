from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from .models import Producto, Categoria
from .forms import RegistroForm, ProductoForm, CategoriaForm

def is_admin(user):
    return user.is_staff

# Vistas públicas
def home(request):
    productos_destacados = Producto.objects.filter(
        activo=True
    ).select_related('categoria').order_by('-fecha_creacion')[:6]
    
    categorias_activas = Categoria.objects.filter(
        activa=True, 
        productos__isnull=False
    ).distinct()[:5]
    
    return render(request, 'catalogo/home.html', {
        'productos_destacados': productos_destacados,
        'categorias': categorias_activas
    })

@login_required(login_url='catalogo:login')
def catalogo(request):
    categorias = Categoria.objects.filter(activa=True)
    productos = Producto.objects.filter(activo=True).select_related('categoria')
    
    # Filtros
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__nombre__icontains=query)
        )
    
    # Ordenamiento
    orden = request.GET.get('orden', '-fecha_creacion')
    productos = productos.order_by(orden)
    
    # Paginación
    paginator = Paginator(productos, 12)
    page = request.GET.get('page')
    productos = paginator.get_page(page)
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'current_categoria': categoria_id,
        'query': query,
        'orden': orden
    }
    
    return render(request, 'catalogo/catalogo.html', context)

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto.objects.select_related('categoria'), 
                                id=producto_id, activo=True)
    
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        activo=True
    ).exclude(id=producto.id)[:4]
    
    return render(request, 'catalogo/detalle_producto.html', {
        'producto': producto,
        'productos_relacionados': productos_relacionados
    })

# Autenticación
def registro(request):
    if request.user.is_authenticated:
        return redirect('catalogo:home')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido a Glam.')
            return redirect('catalogo:home')
    else:
        form = RegistroForm()
    
    return render(request, 'catalogo/registro.html', {'form': form})

def inicio_sesion(request):
    if request.user.is_authenticated:
        return redirect('catalogo:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'catalogo:home')
            messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'catalogo/login.html')

@login_required
def cerrar_sesion(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('catalogo:home')

# Administración de productos
@user_passes_test(is_admin, login_url='catalogo:no_autorizado')
def lista_productos(request):
    productos = Producto.objects.all().select_related('categoria')
    
    # Filtros
    estado = request.GET.get('estado')
    if estado == 'activo':
        productos = productos.filter(activo=True)
    elif estado == 'inactivo':
        productos = productos.filter(activo=False)
    
    categoria = request.GET.get('categoria')
    if categoria:
        productos = productos.filter(categoria_id=categoria)
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query)
        )
    
    # Ordenamiento
    orden = request.GET.get('orden', '-fecha_creacion')
    productos = productos.order_by(orden)
    
    # Paginación
    paginator = Paginator(productos, 20)
    page = request.GET.get('page')
    productos = paginator.get_page(page)
    
    categorias = Categoria.objects.filter(activa=True)
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'estado': estado,
        'categoria_seleccionada': categoria,
        'query': query,
        'orden': orden
    }
    
    return render(request, 'catalogo/lista_productos.html', context)

@user_passes_test(is_admin, login_url='catalogo:no_autorizado')
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.nombre}" agregado exitosamente.')
            return redirect('catalogo:lista_productos')
    else:
        form = ProductoForm()
    
    return render(request, 'catalogo/agregar_producto.html', {'form': form})

@user_passes_test(is_admin, login_url='catalogo:no_autorizado')
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto "{producto.nombre}" actualizado correctamente.')
            return redirect('catalogo:lista_productos')
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'catalogo/editar_producto.html', {
        'form': form,
        'producto': producto
    })

@user_passes_test(is_admin, login_url='catalogo:no_autorizado')
@require_POST
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    nombre = producto.nombre
    
    try:
        producto.delete()
        messages.success(request, f'Producto "{nombre}" eliminado correctamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar el producto: {str(e)}')
    
    return redirect('catalogo:lista_productos')

# Administración de categorías
@user_passes_test(is_admin, login_url='catalogo:no_autorizado')
def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'catalogo/lista_categorias.html', {'categorias': categorias})

@user_passes_test(is_admin, login_url='catalogo:no_autorizado')
def agregar_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" agregada exitosamente.')
            return redirect('catalogo:lista_categorias')
    else:
        form = CategoriaForm()
    
    return render(request, 'catalogo/agregar_categoria.html', {'form': form})

@user_passes_test(is_admin, login_url='catalogo:no_autorizado')
def editar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" actualizada correctamente.')
            return redirect('catalogo:lista_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    
    return render(request, 'catalogo/editar_categoria.html', {
        'form': form,
        'categoria': categoria
    })

@user_passes_test(is_admin, login_url='catalogo:no_autorizado')
@require_POST
def eliminar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    nombre = categoria.nombre
    
    try:
        categoria.delete()
        messages.success(request, f'Categoría "{nombre}" eliminada correctamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar la categoría: {str(e)}')
    
    return redirect('catalogo:lista_categorias')

# Errores
def no_autorizado(request):
    messages.error(request, 'No tienes permiso para acceder a esta página.')
    return render(request, 'catalogo/403_no_autorizado.html', status=403)