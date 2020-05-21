from django.contrib import admin
from django.urls import include, path
from rating_app import views
from django.views.generic import TemplateView

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('', views.home, name='home'),
    path('success/', views.success, name='success'),
    path('rate/', views.rate, name='rate'),
    path('djangoadmin/', admin.site.urls),
    path('evaluation_progress/', views.evaluation_progress),
    path('details/', views.details),
    path('overall/', views.overall),
    path('database/', views.database),
    path('delete_database/', views.delete_database),
    path('save_database/',views.save_database),
    path('save_database_1/', views.save_database_1),
    path('save_database_2/', views.save_database_2),
    path('update_database/', views.update_database),
    path('admin/', views.admin),
]
