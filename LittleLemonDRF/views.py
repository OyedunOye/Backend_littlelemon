from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .models import MenuItem, Category, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CategorySerializer, UserSerializer, UserCartSerializer, UserOrdersSerializer, OrderItemSerializer
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from decimal import Decimal
from django.shortcuts import get_object_or_404



class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # throttle_classes = [AnonRateThrottle, UserRateThrottle]
    # ordering_fields = ['id', 'slug', 'title']

    def get_permissions(self):
        permission_classes = []
        if self.request.method != "GET":
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

# create a special permission class to define privileges for superuser group & admin group. Note that
# this class can be any name but starts with 'Is' to match naming convention in base permission class.
class IsSuperUserOrManager(permissions.BasePermission):
    def has_permission(self, request, view):

        # privilege for any request for superusers
        if request.user and request.user.is_superuser:
            return True

        # privilege for managers to perform POST, PUT, DELETE & PATCH requests
        if request.user and request.user.groups.filter(name="Manager").exists():
            return request.method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']

        # all other users allowed to perform GET request
        return request.method == 'GET'


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price']
    filterset_fields = ['price']
    search_fields = ['title']
    # authentication_classes = [BasicAuthentication]
    permission_classes = [IsSuperUserOrManager]
    # throttle_classes = [AnonRateThrottle, UserRateThrottle]


class SingleMenuView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class= MenuItemSerializer
    permission_classes = [IsSuperUserOrManager]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]


class ManagerUsersView(generics.ListCreateAPIView):
    permission_classes = [IsSuperUserOrManager]
    serializer_class=UserSerializer

    def get_queryset(self):
        manager_group = Group.objects.get(name="Manager")
        return manager_group.user_set.all()

    def post(self, request):
        username = request.data.get("username")
        user = get_object_or_404(User, username=username)
        manager_group = Group.objects.get(name="Manager")
        manager_group.user_set.add(user)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        username = request.data.get("username")
        user = get_object_or_404(User, username=username)
        manager_group = Group.objects.get(name="Manager")
        manager_group.user_set.remove(user)
        return Response({"message": "User removed from the manager group"}, status=status.HTTP_200_OK)


class SingleManagerUserView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsSuperUserOrManager]
    serializer_class = UserSerializer

    def get_queryset(self):
        manager_group = Group.objects.get(name="Manager")
        queryset = User.objects.filter(groups=manager_group)
        return queryset


class DeliveryCrewUsersView(generics.ListCreateAPIView, generics.DestroyAPIView):
    permission_classes = [IsSuperUserOrManager]
    serializer_class = UserSerializer

    def get_queryset(self):
        delivery_group = Group.objects.get(name="delivery_crew")
        return delivery_group.user_set.all()

    def post(self, request):
        username = request.data.get("username")
        user = get_object_or_404(User, username=username)
        delivery_group = Group.objects.get(name="delivery_crew")
        delivery_group.user_set.add(user)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        username = request.data.get("username")
        user = get_object_or_404(User, username=username)
        delivery_group = Group.objects.get(name="delivery_crew")
        delivery_group.user_set.remove(user)
        return Response({"message": "User removed from the delivery crew group"}, status=status.HTTP_200_OK)


class SingleDeliveryCrewUserView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsSuperUserOrManager]
    serializer_class = UserSerializer

    def get_queryset(self):
        delivery_group = Group.objects.get(name="delivery_crew")
        queryset = User.objects.filter(groups=delivery_group)
        return queryset


class CustomerCartView(generics.ListCreateAPIView):
    serializer_class = UserCartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)

    def perform_create(self, serializer):
        menuitem = self.request.data.get('menuitem')
        quantity = self.request.data.get('quantity')
        unit_price = MenuItem.objects.get(pk=menuitem).price
        quantity = int(quantity)
        price = quantity * unit_price
        serializer.save(user=self.request.user, unit_price=unit_price, price=price)

        def delete(self,request):
            user = self.request.user
            Cart.objects.filter(user=user).delete()
            return Response (status=status.HTTP_204_NO_CONTENT)

class OrdersView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserOrdersSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def perform_create(self, serializer):
        cart_items = Cart.objects.all().filter(user=self.request.user).all()
        menuitem_count = cart_items.count()
        if menuitem_count == 0:
            return Response({"message": "no item in cart"})

        total = self.calculate_total(cart_items)
        order = serializer.save(user=self.request.user, total=total)

        for cart_item in cart_items:
            OrderItem.objects.create(
                menuitem = cart_item.menuitem,
                qunatity = cart_item.quantity,
                unit_price= cart_item.unit_price,
                price = cart_item.price,
                order=order
            )
            cart_item.delete()

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="manager").exists():
            return Order.objects.all()
        elif user.groups.filter(name="delivery crew").exists():
            return Order.objects.all().filter(delivery_crew=user)
        return Order.objects.filter(user=user)

    def calculate_total(self, cart_items):
        total = Decimal(0)
        for item in cart_items:
            total += item.price
        return total

class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserOrdersSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='manager').exists():
            return Order.objects.all()
        elif user.groups.filter(name='delivery crew').exists():
            return Order.objects.all.filter(delivery_crew=self.request.user)
        return Order.objects.filter(user=user)