from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("user_listing",views.user_listing, name="user_listing"),
    path("create_listing",views.create_listing,name="create_listing"),
    path('listing/<int:listing_id>/', views.listing_description, name='listing_description'),
    path('listing/<int:listing_id>/place_bid/', views.place_bid, name='place_bid'),
]
