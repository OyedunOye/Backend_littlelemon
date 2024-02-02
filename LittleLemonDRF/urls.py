from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('category', views.CategoriesView.as_view()),
    path('menu-items', views.MenuItemsView.as_view()),
    path('cart', views.CartView.as_view()),
    path('order', views.OrderView.as_view()),
    path('order-item', views.OrderItemView.as_view()),
    # path('users', views.User.),
    path('api-token-auth', obtain_auth_token),
]