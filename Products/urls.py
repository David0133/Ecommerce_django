from django.urls import path
from StoreDoor import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('',views.products,name='products'),
    path('<slug:category_slug>/',views.products,name='products_by_category'),
    path("<slug:category_slug>/<slug:product_slug>/",views.product_detail,name='product_detail'),
    path('search',views.search,name='search'),
] 