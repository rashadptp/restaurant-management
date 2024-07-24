from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView
from .views import ContactUsView, submitted_successfully
from django.conf import settings
from django.conf.urls.static import static
from .views import RegisterCustomerView, RegisterStaffView, RegisterAdminView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutUsView.as_view(), name='about_us'),
    path('contact/', ContactUsView.as_view(), name='contact_us'),
    path('menu/', MenuListView.as_view(), name='menu_list'),

    #############  DASHBOARD VIEWS  ########################
    path('customer/dashbaord/', CustomerDashboardView.as_view(), name='customer_dashboard'),
    path('staff/dashboard/', StaffDashboardView.as_view(), name='staff_dashboard'),
    path('admin1/', AdminDashboardView.as_view(), name='admin_dashboard'),
    
    ############# CUSTOMER URLS       #######################
    path('order/', PlaceOrderView.as_view(), name='place_order'),
    path('reserve/', ReserveTableView.as_view(), name='reserve_table'),
    path('active_orders/', ActiveOrdersViewCust.as_view(), name='cust_active_orders'),
    path('completed_orders/', CompletedOrdersView.as_view(), name='completed_orders'),
    path('cust_reservations/', ReservationCustView.as_view(), name='reservation_cust'),
    path('profile/', view_profile, name='view_profile'),path('profile/', view_profile, name='view_profile'),
    path('submitted-successfully/',submitted_successfully, name='submitted_successfully'),
    path('read-stories/', ReadStoriesView.as_view(), name='read_stories'),
    path('menu/search/', MenuSearchView.as_view(), name='menu_search'),
    path('cancel-reservation/', CancelReservationView.as_view(), name='cancel_reservation'),
    path('customer/redeem-gift/', RedeemGiftView.as_view(), name='redeem_gift'),
    path('confirm-redeem-gift/', ConfirmRedeemGiftView.as_view(), name='confirm_redeem_gift'),
    path('recommendations/<int:user_id>/', get_recommendationss, name='get_recommendations'),


    ##############  STAFF URLS
    path('orders/', ViewOrdersView.as_view(), name='view_orders'),
    path('toggle-availability/', ToggleAvailabilityView.as_view(), name='toggle_availability'),
    path('active-orders/', ActiveOrdersView.as_view(), name='active_orders'),
    path('update-order-status/<int:pk>/', UpdateOrderStatusView.as_view(), name='update_order_status'),

    #############  ADMIN URLS          ###########################
    path('menu/add/', MenuItemCreateView.as_view(), name='menu_item_add'),
    # path('menu/<int:pk>/edit/', MenuItemUpdateView.as_view(), name='menu_item_edit'),
    path('menu/<int:pk>/delete/', MenuItemDeleteView.as_view(), name='menu_item_delete'),
    path('admin1/add_table/', AddTableView.as_view(), name='add_table'),
    path('admin1/tables/', TableListView.as_view(), name='table_list'),
    path('admin1/revenue/', AdminRevenueView.as_view(), name='admin_revenue'),
    path('menu/update/<int:pk>/', MenuItemUpdateView.as_view(), name='menu_item_update'),
    path('admin1/menu/', AdminMenuView.as_view(), name='admin_menu'),
    path('menu/<int:pk>/delete/', MenuItemDeleteView.as_view(), name='menu_item_delete'),
    path('recommendations/', RecommendationsView.as_view(), name='recommendations'),
    # path('predict/', predict_demand, name='predict_demand'),
    path('predict/', PredictView.as_view(), name='predict'),
    path('admin1/cancel-reservation',CancelAdminReservationView.as_view(),name='cancel_reservation_admin'),




    ###############  LOGIN SIGNUP URLS  #######################
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', RegisterCustomerView.as_view(), name='signup'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



urlpatterns += [
    path('register/customer/', RegisterCustomerView.as_view(), name='register_customer'),
    path('register/staff/', RegisterStaffView.as_view(), name='register_staff'),
    path('register/admin/', RegisterAdminView.as_view(), name='register_admin'),
]
