from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
     path('dashboard/', views.dashboard, name='dashboard'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
     path('forgotpassword/', views.forgotPassword, name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),
    path('my_orders/',views.myOrders,name='my_orders'),
    path('edit_profile/',views.edit_profile,name='edit_profile'),
    path('change_password/',views.changePassword,name='change_password'),
    path('order_detail/<int:order_id>/',views.orderDetail,name='order_detail'),

]