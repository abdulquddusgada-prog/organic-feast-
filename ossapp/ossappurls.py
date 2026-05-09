from django.urls import path
from . import views

urlpatterns=[
    path('',views.index,name='index'),
    path('about/',views.about,name='about'),
    path('product/',views.productPage,name='product'),
    path('register/', views.register, name='register'),
    path('login/', views.signin, name='login'),
    path('ownerdashboard',views.ownerdashboard,name='ownerdashboard'),
    path('ownerlogin',views.ownersignin,name='ownerlogin'),
    path('user/',views.user, name='user'),
    path('orders/',views.orders, name='orders'),
    path('viewsorders',views.vieworders,name='vieworders'),
    path('logout/', views.signout, name='logout'),
    path('buynow/', views.buynow, name='buynow'),
    path('checkout/', views.checkout, name='checkout'),
    path('changepass/', views.changepass, name='changepass'),
    path('mycart/', views.mycart, name='mycart'),
    path('update_cart/',views.update_cart, name='update_cart'),
    path('search/', views.search_results, name='search_results'),
    path('add-delivery-person/', views.add_delivery_person, name='add_delivery_person'),
    path('delivery-persons/', views.delivery_persons, name='delivery_persons'),
    path('transfer-money/', views.transfer_money, name='transfer_money'),
    path('suggestions/', views.suggestion_view, name='suggestions'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('deliveryboylogin/', views.deliveryboylogin, name='deliveryboylogin'),
    path('deliveryboydsb/', views.deliveryboydsb, name='deliveryboydsb'),
    path('add_to_wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('add_review/<int:product_id>/', views.add_review, name='add_review'),

]