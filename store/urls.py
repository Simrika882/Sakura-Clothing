from django.urls import path
from . import views 
from store.views import * 
urlpatterns = [
    path('', views.index, name='index'),
    path('category/<str:category_name>/', views.category_view, name='category_view'),
    path('clothes/', views.clothes, name='clothes'),
    path('jeans/', views.jeans, name='jeans'),
    path('shoes/', views.shoes, name='shoes'),
    path('accessories/', views.accessories, name='accessories'),
    path('cart/', views.cart, name='cart'),
	path('checkout/', views.checkout, name='checkout'),
	path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('search/', views.search, name='search'),
    path('invoice/<int:invoice_id>/', views.invoice_view, name='invoice_view'),
]