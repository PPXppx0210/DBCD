"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, re_path
from ocean_current import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'), 
    path('home/', views.home, name='home'),
    path('home/formation/', views.formation, name='formation'),
    path('home/classification/', views.classification, name='classification'),
    path('home/impact/', views.impact, name='impact'),
    path('home/mainoc/', views.mainoc, name='mainoc'),
    path('personal/', views.personal, name='personal'),
    path('logout/', views.user_logout, name='logout'),
    path('dataimport/', views.dataimport, name='dataimport'),
    path('datasearch/', views.datasearch, name='datasearch'),
    path('edit/<int:data_id>/', views.edit_data, name='edit'),
    path('dataanalyse/', views.dataanalyse, name='dataanalyse'),
    re_path(r'^$', views.index, name='index'),  
]
