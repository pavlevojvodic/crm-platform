from django.urls import path
from . import views

urlpatterns = [
    path('log_in', views.log_in),
    path('dashboard', views.dashboard),
    path('change_customer_stage', views.change_customer_stage),
    path('add_customer', views.add_customer),
    path('add_customer_note', views.add_customer_note),
    path('delete_customer_note', views.delete_customer_note),
    path('customer/<int:customer_id>/', views.load_customer_data),
    path('edit_customer', views.edit_customer),
    path('send_email', views.send_email),
    path('users/<int:company_id>/', views.get_users),
    path('add_user', views.add_user),
    path('contacts/<int:company_id>/', views.contacts),
    path('add_affiliate', views.add_affiliate),
    path('notifications', views.notifications),
    path('mark_notifications_read', views.mark_notifications_read),
    path('excel_report', views.excel_report),
]
