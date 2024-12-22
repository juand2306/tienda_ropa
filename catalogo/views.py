from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Categoria
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .forms import RegistroForm, ProductoForm


# Create your views here.
@login_required
def catalogo(request):
    categorias = Categoria.objects.all()
    categoria_id = request.GET.get('categoria')

    if categoria_id:
        productos = Producto.objects.filter(categoria_id=categoria_id)
    else:
        productos = Producto.objects.all()

    return render(request, 'catalogo/catalogo.html', {
        'productos': productos,
        'categorias': categorias,
    })

def home(request):
    return render(request, 'catalogo/home.html')

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'catalogo/registro.html', {'form': form})

def inicio_sesion(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'catalogo/login.html', {'form': form})

def cerrar_sesion(request):
    logout(request)
    return redirect('home')

# Función para verificar si es administrador
def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin, login_url='/no-autorizado/')
def agregar_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        imagen = request.FILES.get('imagen')  # Capturar la imagen cargada

        # Validaciones básicas
        if nombre and descripcion and precio and imagen:
            try:
                precio = float(precio)  # Asegurarse de que el precio sea numérico
                Producto.objects.create(
                    nombre=nombre,
                    descripcion=descripcion,
                    precio=precio,
                    imagen=imagen
                )
                messages.success(request, "El producto fue agregado exitosamente.")
                return redirect('lista_productos')
            except ValueError:
                messages.error(request, "El precio debe ser un número válido.")
        else:
            messages.error(request, "Por favor, completa todos los campos.")

    return render(request, 'catalogo/agregar_producto.html')

@user_passes_test(is_admin)
def lista_productos(request):
    list_productos = Producto.objects.all()  # Obtenemos todos los productos
    return render(request, 'catalogo/lista_productos.html', {'list_productos': list_productos})

@user_passes_test(is_admin)
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'catalogo/editar_producto.html', {'form': form})

@user_passes_test(is_admin)
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        producto.delete()
        return redirect('lista_productos')
    return render(request, 'catalogo/eliminar_producto.html', {'producto': producto})

def no_autorizado(request):
    return render(request, '403_no_autorizado.html', {})
