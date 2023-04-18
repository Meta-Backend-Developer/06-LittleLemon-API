from django.urls import path
from . import views


urlpatterns = [
    path('menu-items/', views.MenuItemView.as_view()),
    path('menu-items/<int:pk>/', views.SingleItemView.as_view()),
    path('groups/manager/users/', views.ManagerUsersView.as_view()),
    path('groups/manager/users/<int:pk>/', views.ManagerSingleUserView.as_view()),
    path('groups/delivery-crew/users/', views.DeliveryCrewManagement.as_view()),
    path('groups/delivery-crew/users/<int:pk>/', views.DeliveryCrewManagementSingleView.as_view()),
    path('cart/menu-items/', views.CustomerCart.as_view()),
    path('orders/', views.Ordersview.as_view()),
    path('orders/<int:pk>/', views.SingleOrderview.as_view()),
]
