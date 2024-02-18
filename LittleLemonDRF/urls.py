from django.urls import path
from . import views
# from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('category', views.CategoriesView.as_view()),
    path('menu-items', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuView.as_view()),
    path('groups/manager/users', views.ManagerUsersView.as_view()),
    path('groups/manager/users/<int:pk>', views.SingleManagerUserView.as_view()),
    path('groups/delivery-crew/users', views.DeliveryCrewUsersView.as_view()),
    path('groups/delivery-crew/users/<int:pk>', views.SingleDeliveryCrewUserView.as_view()),
    path('cart/menu-items', views.CustomerCartView.as_view()),
    path('orders', views.OrdersView.as_view()),
    path('cart/orders', views.OrdersView.as_view()),
    path('orders/<int:pk>', views.SingleOrderView.as_view()),
    path('cart/orders/<int:pk>', views.SingleOrderView.as_view()),
    # path('api-token-auth', obtain_auth_token),
]