from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from .models import MenuItem, Category, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CategorySerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from rest_framework.response import Response
from rest_framework import status


class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price']
    filterset_fields = ['price']
    search_fields = ['category']
    # authentication_classes = [BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    
    def get_permission(self, request):
        if(self.request.method == "GET"):
            if request.user.groups.filter(name="Customer").exists():
                return [IsAuthenticated]
            elif request.user.groups.filter(name="delivery_crew").exists():
                return [IsAuthenticated]
            elif request.user.groups.filter(name="Manager").exists():
                return [IsAuthenticated]
            else:
                return []
            
    def post(self, request):
        # if request.user.IsAuthenticated:
            if(self.request.method == "POST"):
                if request.auth.groups.filter(name="Customer").exists():
                    return Response({'message': 'You are unauthorized to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
                if request.auth.groups.filter(name="delivery_crew").exists():
                    return Response({'message': 'You are unauthorized to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
                if request.auth.groups.filter(name="Manager").exists():
                    return self.create(request)
                    # serializer = MenuItemSerializer(data=request.data)
                    # if serializer.is_valid():
                    #     serializer.save()
                    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

     
class CartView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    
   
class OrderView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def get_permissions(self):
        if(self.request.method=='GET'):
            return []

        return [IsAuthenticated()]
    
class OrderItemView(generics.ListCreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    
    def get_permissions(self):
        if(self.request.method=='GET'):
            return []

        return [IsAuthenticated()]