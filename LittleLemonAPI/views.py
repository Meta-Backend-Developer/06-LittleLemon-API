from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from decimal import Decimal

from .models import MenuItem, Category, OrderItem, Cart, Order
from .serializers import MenuItemSerializer, CategorySerializer, UserSerializer, UserCartSerializer, UserOrdersSerializer



class MenuItemView(generics.ListAPIView, generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    search_fields = ['title', 'category__title']
    ordering_fields = ['price']
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]

class SingleItemView(generics.RetrieveUpdateDestroyAPIView, generics.RetrieveAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]
    

class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]
    
    

class ManagerUsersView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        manager_group = Group.objects.get(name='Manager')
        queryset = User.objects.filter(groups=manager_group)
        return queryset

    def perform_create(self, serializer):
        manager_group = Group.objects.get(name='Manager')
        user = serializer.save()
        user.groups.add(manager_group)


class ManagerSingleUserView(generics.RetrieveDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        manager_group = Group.objects.get(name='Manager')
        queryset = User.objects.filter(groups=manager_group)
        return queryset
    

class DeliveryCrewManagement(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        delivery_group = Group.objects.get(name='Delivery Crew')
        queryset = User.objects.filter(groups=delivery_group)
        return queryset

    def perform_create(self, serializer):
        delivery_group = Group.objects.get(name='Delivery Crew')
        user = serializer.save()
        user.groups.add(delivery_group)


class DeliveryCrewManagementSingleView(generics.RetrieveDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        delivery_group = Group.objects.get(name='Delivery Crew')
        queryset = User.objects.filter(groups=delivery_group)
        return queryset


class CustomerCart(generics.ListCreateAPIView):
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
        serializer.save(user=self.request.user, price=price)

    def delete(self, request):
        user = self.request.user
        Cart.objects.filter(user=user).delete()
        return Response(status=204)


class Ordersview(generics.ListCreateAPIView):
    serializer_class = UserOrdersSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def perform_create(self, serializer):
        cart_items = Cart.objects.filter(user=self.request.user)
        total = self.calculate_total(cart_items)
        order = serializer.save(user=self.request.user, total=total)

        for cart_item in cart_items:
            OrderItem.objects.create(
                menuitem=cart_item.menuitem, 
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price, 
                price=cart_item.price, 
                order=order
                )
            cart_item.delete()

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        return Order.objects.filter(user=user)


    def calculate_total(self, cart_items):
        total = Decimal(0)
        for item in cart_items:
            total += item.price
        return total


class SingleOrderview(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserOrdersSerializer
    permission_classes = [IsAuthenticated]
    delivery_crew = Order.delivery_crew
    status = Order.status

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        return Order.objects.filter(user=user)

    