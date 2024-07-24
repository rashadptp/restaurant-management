from django.contrib.auth import views as auth_views
from django.urls import path,include
from django.contrib import admin
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('resto.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    

]
