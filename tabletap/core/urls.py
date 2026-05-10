from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.landing_page, name='landing'),
    path('signup/', views.signup_view, name='signup'),
    path("validate-signup-step1/", views.validate_signup_step1, name="validate_signup_step1"),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # path('complete-registration/', views.complete_registration_view, name='complete_registration'),
    path('complete-registration/', views.complete_registration_view, name='complete_registration'),

    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('tables/', views.table_management, name='table_management'),
    path('tables/delete/<int:table_id>/', views.delete_table, name='delete_table'),

    path('orders/', views.order_management, name='order_management'),
    path('orders/update-status/', views.update_order_status, name='update_order_status'),

    path('menu/', views.menu_management, name='menu_management'),

    path('menu/add/', views.menu_add, name='menu_add'),
    path('menu/delete/<int:menu_id>/', views.menu_delete, name='menu_delete'),
    path('menu/<int:menu_id>/edit/', views.menu_edit, name='menu_edit'),
    
    path('menu/toggle/<int:menu_id>/', views.menu_toggle, name='menu_toggle'),

    path('menu/item/add/', views.menu_item_add, name='menu_item_add'),
    path('menu/item/edit/<int:item_id>/', views.menu_item_edit, name='menu_item_edit'),
    path('menu/item/delete/<int:item_id>/', views.menu_item_delete, name='menu_item_delete'),

    path('menu/category/add/', views.menu_category_add, name='menu_category_add'),
    path('menu/category/edit/<int:category_id>/', views.menu_category_edit, name='menu_category_edit'),
    path('menu/category/delete/<int:category_id>/', views.menu_category_delete, name='menu_category_delete'),
    path('menu/item/toggle/<int:item_id>/', views.menu_item_toggle, name='menu_item_toggle'),

    path('menu/<int:table_id>/', views.customer_menu, name='customer_menu'),
    path('submit_order/<int:table_id>/', views.submit_order, name='submit_order'),
]
