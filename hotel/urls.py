from django.contrib import admin
from django.urls import path, include
from django.conf import settings # IMPORTANTE
from django.conf.urls.static import static # IMPORTANTE
from django.contrib.auth import views as auth_views 
from django.contrib.admin.forms import AdminAuthenticationForm

AdminAuthenticationForm.error_messages['invalid_login'] = "Usuario y/o clave incorrecto."

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('reservas.urls')),
    # Esta línea habilita login, logout, etc.
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]

# Esto conecta la URL /media/ con la carpeta física media/
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)