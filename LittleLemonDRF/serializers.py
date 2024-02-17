from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order, OrderItem
# from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.models import User
from datetime import datetime

class CategorySerializer (serializers.ModelSerializer):
    class Meta:
         model = Category
         fields = ['id','title']
         
class MenuItemSerializer(serializers.ModelSerializer):
    # category_id = serializers.IntegerField(write_only=True)
    # category = CategorySerializer(read_only=True)
    category =serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']
        
class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(write_only=True, default=datetime.now)
    email = serializers.EmailField(required=False)
    date_joined_format = serializers.SerializerMethodField(source='date_joined')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'date_joined_format']

    def get_date_joined_format(self, obj):
        return obj.date_joined.strftime('%Y-%m-%d')


class UserCartSerializer(serializers.ModelSerializer):
    # menu = serializers.CharField(write_only=True)
    # menuitem = MenuItemSerializer(read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), default=serializers.CurrentUserDefault())
    # unit_price = MenuItemSerializer.field['price']

    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'quantity', 'unit_price', 'price']
        extra_kwargs = {
            # 'user': {'read_only': True},
            # 'unit_price': {'read_only': True},
            'price': {'read_only': True}
        }


class OrderItemSerializer(serializers.ModelSerializer):
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, source='menuitem.price', read_only=True)
    price = serializers.DecimalField(max_digits=6,decimal_places=2, read_only=True)
    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']
        extra_kwargs = {
            'menuitem' : {'read_only': True}
        }

class UserOrdersSerializer(serializers.ModelSerializer):
    date=serializers.DateField(write_only=True, default=datetime.now)
    date_format = serializers.SerializerMethodField(source='date')
    order_items = OrderItemSerializer(many=True, read_only=True, source="order")
    user = serializers.PrimaryKeyRelatedField(
            queryset=User.objects.all(),
            default=serializers.CurrentUserDefault()
    )
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'date_format', 'order_items']
        extra_kwargs = {
            'total' : {'read_only': True}
        }
        
    def get_date_format(self, obj):
        return obj.date.strftime('%Y-%m-%d')

    def get_order_items(self, obj):
        order_items = OrderItem.objects.filter(order=obj)
        serializer = OrderItemSerializer(order_items, many=True, context={'request': self.context['request']})
        return serializer.data
