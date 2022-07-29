from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home' ),
    path('<payement>/command', views.command, name='command'),
    path('<int:category_id>/category', views.category, name ='category'),
    path('article/<int:article_id>/details', views.details, name ='details'),
    path('article/<int:article_id>/panier', views.add_panier, name ='panier'),
    path('panier', views.panier, name ='voir_panier'),
    #path('panier', views.PanierView.as_view(), name ='voir_panier'),
    path('article/<int:article_id>/favorit', views.add_favorite, name ='add_favorite'),
    path('favorit', views.favorit, name ='favorit'),
    path('about', views.about, name ='about'),
    path('article/<int:article_id>/delete', views.delete, name ='delete'),
    path('paypal-return/', views.PaypalReturnView.as_view(), name='paypal-return'),
    path('paypal-cancel/', views.PaypalCancelView.as_view(), name='paypal-cancel'),
    path('seepaypal/', views.PaypalFormView.as_view(), name='paypal-form'),
    
]