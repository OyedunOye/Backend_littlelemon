from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order, OrderItem
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.models import User

class CategorySerializer (serializers.ModelSerializer):
    class Meta:
         model = Category
         fields = ['id','title']
         
class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']
        
class CartSerializer(serializers.ModelSerializer):
    
    menuitem = MenuItemSerializer()
    
    items_price = serializers.SerializerMethodField(method_name='calc_price')
    user = serializers.PrimaryKeyRelatedField(
            queryset=User.objects.all(),
            default=serializers.CurrentUserDefault()
    )
    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'quantity', 'items_price']
    def calc_price(self, product:Cart):
        return product.unit_price * product.quantity
        
class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
            queryset=User.objects.all(),
            default=serializers.CurrentUserDefault()
    )
    class Meta:
        model = Order
        fields = ['user', 'delivery_crew', 'status', 'total', 'date']
    
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']
        
# class RatingSerializer (serializers.ModelSerializer):
#     user = serializers.PrimaryKeyRelatedField(
#             queryset=User.objects.all(),
#             default=serializers.CurrentUserDefault()
#     )

#     class Meta:
#         model = Rating
#         fields = ['user', 'menuitem_id', 'rating']

#         validators = [
#             UniqueTogetherValidator(
#                 queryset=Rating.objects.all(),
#                 fields=['user', 'menuitem_id']
#             )
#         ]

#         extra_kwargs = {
#             'rating': {'min_value': 0, 'max_value':5},
#         }