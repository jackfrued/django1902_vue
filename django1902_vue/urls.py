from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from poll2 import views

urlpatterns = [
    path('', views.index),
    path('subjects/', views.show_subjects),
    path('teachers/', views.show_teachers),
    path('praise/', views.praise_or_criticize),
    path('criticize/', views.praise_or_criticize),
    path('login/', views.login),
    path('register/', views.register),
    path('logout/', views.logout),
    path('captcha/', views.get_captcha),
    path('mobile/', views.get_mobile_code),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:

    import debug_toolbar

    urlpatterns.insert(0, path('__debug__/', include(debug_toolbar.urls)))
