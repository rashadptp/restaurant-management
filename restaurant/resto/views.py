# resto/views.py

from django.views.generic import TemplateView, ListView, CreateView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect,render
from django.urls import reverse_lazy,reverse
from django.contrib.auth.models import Group,User
from .models import MenuItem, Table, Order, Reservation,Section,OrderItem,CoinTransaction
from .mixins import GroupRequiredMixin
from django.views import View
from django.db import models
from django.contrib.auth.models import Group, User
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
import re,random,string
from django.shortcuts import render, redirect
from django.views import View
import pandas as pd
import joblib
from .forms import PredictionForm

from datetime import date, datetime
from django.utils import timezone
from .recommendations import get_recommendations
import pandas as pd
from .utils import send_reservation_confirmation_email
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives


class HomeView(TemplateView):
    template_name = 'resto/home.html'
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.groups.filter(name='Customer').exists():
                return redirect(reverse('customer_dashboard'))
            elif request.user.groups.filter(name='Staff').exists():
                return redirect(reverse('staff_dashboard'))
            elif request.user.groups.filter(name='Admin').exists():
                return redirect(reverse('admin_dashboard'))
        return super().dispatch(request, *args, **kwargs)

class AboutUsView(TemplateView):
    template_name = 'resto/about_us.html'


class ContactUsView(TemplateView):
    
    def get(self, request, *args, **kwargs):
        return render(request, 'resto/contact_us.html')

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        # Send email
        subject = f"Contact Us from {name}"
        message_body = f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\nMessage:\n{message}"
        sender_email = email  # Use customer's email as sender
        recipient_list = ['rashadbackup11@gmail.com']  # Replace with your email address
        
        send_mail(subject, message_body, sender_email, recipient_list, fail_silently=False)

        return redirect(reverse_lazy('submitted_successfully'))
    
def submitted_successfully(request):
    return render(request, 'resto/submitted_successfully.html')

class MenuView(ListView):
    model = MenuItem
    template_name = 'resto/menu.html'
    context_object_name = 'menu_items'

class CustomerDashboardView(LoginRequiredMixin, GroupRequiredMixin, TemplateView):
    template_name = 'resto/customer_dashboard.html'
    group_name = 'Customer'
    def get(self, request, *args, **kwargs):
        user = request.user

        # Calculate total coins
        earned_transactions = CoinTransaction.objects.filter(user=user, transaction_type='earn')
        redeemed_transactions = CoinTransaction.objects.filter(user=user, transaction_type='redeem')

        total_earned = sum(transaction.amount for transaction in earned_transactions)
        total_redeemed = sum(transaction.amount for transaction in redeemed_transactions)

        total_coins = total_earned + total_redeemed

        return render(request, 'resto/customer_dashboard.html', {
            'total_coins': total_coins,
            # Add other context variables as needed
        })
    def get_context_data(self, **kwargs):
        user =self.request.user
        context = super().get_context_data(**kwargs)
        context['active_orders'] = Order.objects.filter(customer=user, is_completed=False)
        context['completed_orders'] = Order.objects.filter(customer=user, is_completed=True)
        context['reservations'] = Reservation.objects.filter(customer=user)
        return context
    
class StaffDashboardView(LoginRequiredMixin, GroupRequiredMixin, TemplateView):
    template_name = 'resto/staff_dashboard.html'
    group_name = 'Staff'
from django.db.models import Sum
class AdminDashboardView(LoginRequiredMixin, GroupRequiredMixin, TemplateView):
    template_name = 'resto/admin_dashboard.html'
    group_name = 'Admin'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_revenue = sum(order.total_amount() for order in Order.objects.filter(status='D'))
        context['total_revenue'] = total_revenue
        # Add additional contexts for other views as needed
        return context



class PlaceOrderView(LoginRequiredMixin, View):
    # template_name = 'resto/place_order.html'
    # success_url = reverse_lazy('read_stories')

    def get(self, request, *args, **kwargs):
        tables = Table.objects.all()
        sections = Section.objects.prefetch_related('menu_items').all()
        return render(request, 'resto/place_order.html', {'sections': sections,'tables':tables})

    def post(self, request, *args, **kwargs):
        customer = request.user
        table_id = request.POST['table']
        items_data = request.POST.getlist('items')
        quantities = request.POST.getlist('quantities')

        # Create Order
        order = Order.objects.create(customer=customer, table_id=table_id, status='P')

        total_amount = 0
        order_items=[]
        for item_id, quantity in zip(items_data, quantities):
            menu_item = MenuItem.objects.get(id=item_id)
            quantity = int(quantity)
            # OrderItem.objects.create(order=order, menu_item=menu_item, quantity=quantity)
            total_amount += menu_item.price * quantity
            order_item = OrderItem.objects.create(order=order, menu_item=menu_item, quantity=quantity)
            order_items.append(order_item)
        order.total_amount = total_amount
        order.save()
        
        CoinTransaction.objects.create(user=customer, amount=10, transaction_type='earn')

          # Prepare the email content
        email_subject = 'Order Confirmation'
        text_content = f'Dear {customer.username},\n\nYour order has been placed successfully. Here are the details:\n\n'
        html_content = f'<p>Dear {customer.username},</p><p>Your order has been placed successfully. Here are the details:</p><ul>'

        for order_item in order_items:
            text_content += f'{order_item.menu_item.name} - Quantity: {order_item.quantity}\n'
            html_content += f'<li>{order_item.menu_item.name} - Quantity: {order_item.quantity}</li>'

        text_content += '\nThank you for your order! Please be patient while we prepare your food. We will notify you once it\'s ready.\n\nBest regards,\nCravehouse Team'
        html_content += '</ul><p>Thank you for your order! Please be patient while we prepare your food. We will notify you once it\'s ready.</p><p>Best regards,<br>Cravehouse Team</p>'

        # Send confirmation email
        email = EmailMultiAlternatives(
            email_subject,
            text_content,
            'your-email@gmail.com',  # Your verified email address
            [customer.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        
        
        return redirect('read_stories')
         
    
    

    # def get_recommendations(self, user):
    #     import joblib
    #     import pandas as pd
    #     # Load the trained model
    #     model = joblib.load('resto/order_predictor.pkl')

    #     # Collect the user's past orders
    #     past_orders = Order.objects.filter(customer=user)
    #     past_items = []
    #     for order in past_orders:
    #         order_items = OrderItem.objects.filter(order=order)
    #         for item in order_items:
    #             past_items.append({
    #                 'customer_id': user.id,
    #             })

    #     # Prepare the input data
    #     input_data = pd.DataFrame(past_items)

    #     # Check if input_data is empty (i.e., the user has no past orders)
    #     if input_data.empty:
    #         return []  # Return an empty list or some default recommendations

    #     # Predict the menu items
    #     predictions = model.predict(input_data)

    #     # Get the top recommendations
    #     recommended_items_ids = pd.Series(predictions).value_counts().index[:5]  # Top 5 recommendations

    #     # Fetch the MenuItem objects for the recommended items
    #     recommended_menu_items = MenuItem.objects.filter(id__in=recommended_items_ids.tolist())

    #     return recommended_menu_items


@method_decorator(csrf_exempt, name='dispatch')
class ReserveTableView(LoginRequiredMixin, View):
    # template_name = 'resto/reserve_table.html'
    # success_url = reverse_lazy('reservation_cust')

    def get(self, request, *args, **kwargs):
        tables = Table.objects.all()
        return render(request, 'resto/reserve_table.html', {'tables': tables})

    def post(self, request, *args, **kwargs):
        customer = self.request.user
        table_id = request.POST.get('table')
        date_today = date.today()
        reservation_date = request.POST.get('reservation_date')
        reservation_start_time = request.POST.get('reservation_start_time')
        reservation_end_time = request.POST.get('reservation_end_time')

        reservation_date_obj = timezone.datetime.strptime(reservation_date, '%Y-%m-%d').date()

        # Check if the selected table is available for the chosen time range
        if reservation_date_obj < date_today:
            messages.error(request, 'Past Date is not valid for Booking!')
            return render(request, 'resto/reserve_table.html', {'tables': Table.objects.all()})

        if Reservation.objects.filter(table_id=table_id, reservation_date=reservation_date).filter(
            models.Q(reservation_start_time__lt=reservation_end_time, reservation_end_time__gt=reservation_start_time)
        ).exists():
            messages.error(request, 'This table is already booked for the selected time range. Please choose another time or table.')
            return render(request, 'resto/reserve_table.html', {'tables': Table.objects.all()})

        # If table is available, create reservation
        reservation = Reservation.objects.create(
            customer=customer,
            table_id=table_id,
            reservation_date=reservation_date,
            reservation_start_time=reservation_start_time,
            reservation_end_time=reservation_end_time
        )
        send_mail(
            'Table Reservation Confirmation',
            f'Dear {customer.first_name},\n\nYour table reservation is confirmed for {reservation_date} from {reservation_start_time} to {reservation_end_time}.\n\nThank you!',
            'your-email@gmail.com',
            [customer.email],
            fail_silently=False,
        )

        
        messages.success(request, 'Table reserved successfully.')
        return redirect('reservation_cust')

@method_decorator(csrf_exempt, name='dispatch')
class CancelReservationView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        reservation_id = request.POST.get('reservation_id')
        reservation = Reservation.objects.filter(id=reservation_id, customer=request.user).first()

        reservation.delete()
        messages.success(request, 'Reservation cancelled successfully.')
        return redirect('reservation_cust')
    

class CancelAdminReservationView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        reservation_id = request.POST.get('reservation_id')
        reservation = Reservation.objects.filter(id=reservation_id).first()
        customer=reservation.customer
        date=reservation.reservation_date
        reservation.delete()
        
        send_mail(
                'Reservation Cancelled',
                f'Dear {customer.first_name},\n\nWe are Sorry to say that your reservation for { date } is cancelled due to some reasons.We hope you will choose another date. \n\nThank you for choosing us!',
                'your-email@gmail.com',  # Replace with your email
                [customer.email],
                fail_silently=False,
            )
        messages.success(request, 'vdReservation cancelled successfully.')
        return redirect('/admin1?view=reservations')

class ViewOrdersView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Order
    context_object_name = 'orders'
    group_name = 'Staff'
    template_name = 'resto/view_orders.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('table', 'customer').prefetch_related('items').order_by('-created_at')

class AdminRevenueView(LoginRequiredMixin, GroupRequiredMixin, TemplateView):
    template_name = 'resto/admin_revenue.html'
    group_name = 'Admin'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_revenue = sum(order.total_amount() for order in Order.objects.filter(status='D'))
        context['total_revenue'] = total_revenue
        return context

class RegisterCustomerView(View):

    def get(self, request):
        return render(request,'registration/registercust.html' )

    def post(self, request):
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return render(request, 'registration/registercust.html')
        if len(password1) < 6:
            messages.error(request, "Password must be at least 6 characters long with 1 Uppercase & lowercase & digit")
            return render(request, 'registration/registercust.html')

        if not re.search(r'[A-Z]', password1):
            messages.error(request, "Password must contain at least one uppercase letter & lowercase & digit")
            return render(request, 'registration/registercust.html')

        if not re.search(r'[a-z]', password1):
            messages.error(request, "Password must contain at least one uppercase & lowercase & digit")
            return render(request, 'registration/registercust.html')

        if not re.search(r'\d', password1):
            messages.error(request, "Password must contain at least one digit")
            return render(request, 'registration/registercust.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return render(request, 'registration/registercust.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, 'registration/registercust.html')

        user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=make_password(password1)
        )

        # Add user to Customer group
        customer_group = Group.objects.get(name='Customer')
        customer_group.user_set.add(user)

        messages.success(request, "Registration successful")
        return redirect('login')

class RegisterStaffView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'registration/register.html')

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            return render(request, self.template_name, {'error': 'Passwords do not match'})

        user = User.objects.create_user(username=username, password=password)
        staff_group = Group.objects.get(name='Staff')
        staff_group.user_set.add(user)
        login(request, user)
        return redirect('login')

class RegisterAdminView(CreateView):

    def get(self, request, *args, **kwargs):
        return render(request, 'registration/register.html')

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            return render(request, self.template_name, {'error': 'Passwords do not match'})

        user = User.objects.create_user(username=username, password=password)
        admin_group = Group.objects.get(name='Admin')
        admin_group.user_set.add(user)
        login(request, user)
        return redirect('login')

#############################                  MENU                     ##############################################
class MenuListView(ListView):
    model = Section
    template_name = 'resto/menu_list.html'
    context_object_name = 'sections'

    def get_queryset(self):
        return Section.objects.prefetch_related('menu_items').all()

class MenuItemCreateView(LoginRequiredMixin, View):
    
    def get(self, request, *args, **kwargs):
        sections = Section.objects.all()
        return render(request, 'resto/menu_form.html', {'sections': sections})

    def post(self, request, *args, **kwargs):
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        section_id = request.POST['section']
        is_available = request.POST.get('is_available', 'off') == 'on'

        # Retrieve the Section object
        section = Section.objects.get(id=section_id)

        # Create MenuItem object with section
        MenuItem.objects.create(
            name=name, 
            description=description, 
            price=price, 
            section=section, 
            is_available=is_available
        )
        return redirect('admin_dashboard')
    
class MenuItemUpdateView(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = MenuItem
    fields = ['name', 'description', 'price', 'section', 'is_available'] 
    group_name = 'Admin'

    def get(self, request, *args, **kwargs):
        sections = Section.objects.all()
        menu_item = self.get_object()
        return render(request, 'resto/menu_update.html', {'sections': sections, 'menu_item': menu_item})

    def post(self, request, *args, **kwargs):
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        section_id = request.POST['section']
        section = Section.objects.get(id=section_id)
        item = self.get_object()
        item.name = name
        item.description = description
        item.price = price
        item.section = section
        item.is_available = 'is_available' in request.POST
        item.save()
        return redirect('admin_dashboard')

class MenuItemDeleteView(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    model = MenuItem
    template_name = 'resto/menu_confirm_delete.html'
    success_url = reverse_lazy('admin_dashboard')  # Redirect to admin dashboard after deleting
    group_name = 'Admin'  # Assuming only admins can delete menu items

    def post(self, request, *args, **kwargs):
        item = MenuItem.objects.get(id=self.kwargs['pk'])
        item.delete()
        return redirect('admin_dashboard')
    
####################                         AVAILABILITY CHECK                                           #####################


@method_decorator(csrf_exempt, name='dispatch')
class ToggleAvailabilityView(LoginRequiredMixin, GroupRequiredMixin, View):
    group_name = 'Admin'

    def post(self, request, *args, **kwargs):
        item_id = request.POST.get('item_id')
        item = MenuItem.objects.filter(id=item_id).first()
        item.is_available = not item.is_available
        item.save()
        return JsonResponse({'is_available': item.is_available})

############################                  TABLE ADDING TO ADMIN                             ####################################


class AddTableView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tables = Table.objects.all()
        total_tables = tables.count()
        return render(request, 'resto/add_table.html', {
            'tables': tables,
            'total_tables': total_tables
        })

    def post(self, request, *args, **kwargs):
        number = request.POST['number']
        seats = request.POST['seats']
        Table.objects.create(number=number, seats=seats)
        return redirect('add_table') 

class TableListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Table
    template_name = 'resto/table_list.html'
    context_object_name = 'tables'
    group_name = 'Admin'
    def get(self, request, *args, **kwargs):
        tables = Table.objects.all()
        total_tables = tables.count()
        return render(request, 'resto/table_list.html', {
            'tables': tables,
            'total_tables': total_tables
        })




class AdminDashboardView(LoginRequiredMixin, TemplateView):
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all orders and reservations
        context['orders'] = Order.objects.all().order_by('-created_at')
        context['reservations'] = Reservation.objects.all()
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, 'resto/admin_dashboard.html', context)

#########################                            ACTIVE ORDERS                                               ############################
class ActiveOrdersView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    template_name = 'resto/active_orders.html'
    group_name = 'Staff'
    context_object_name = 'orders'
    
    def get_queryset(self):
        return Order.objects.filter(status='P').select_related('table', 'customer').prefetch_related('items').order_by('-created_at')


class UpdateOrderStatusView(LoginRequiredMixin, View):

    def get(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk)
        return render(request, 'resto/update_order_status.html', {'order': order})

    def post(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk)
        status = request.POST['status']
        order.status = status
        order.save()
        if status == 'D':
            customer = order.customer
            # total_amt=order.total_amount
            send_mail(
                'Your Order is Delivered',
                f'Dear {customer.first_name},\n\nYour order has been delivered. We hope you enjoyed your meal! Please proceed to pay the bill.\n\nThank you for choosing us!',
                'your-email@gmail.com',  # Replace with your email
                [customer.email],
                fail_silently=False,
            )
        return redirect('active_orders')

########################################                           ACTIVE AND COMPLETE ORDERS                          ########################################


class ActiveOrdersViewCust(LoginRequiredMixin, ListView):
    template_name = 'resto/cust_activeorders.html'
    context_object_name = 'cust_active_orders'

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user, status='P').order_by('-created_at')


class CompletedOrdersView(LoginRequiredMixin, ListView):
    template_name = 'resto/cust_completed_orders.html'
    context_object_name = 'completed_orders'

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user, status='D').order_by('-created_at')
###################################                       RESERVATION OF CUSTOMERS VIEW        #########################################
class ReservationCustView(LoginRequiredMixin,ListView):
    template_name = 'resto/cust_reservations.html'
    context_object_name ='reservations'
    def get_queryset(self):
        return Reservation.objects.filter(customer=self.request.user).order_by('-reservation_date')



# def get_available_times(request):
#     date_str = request.GET.get('date')
#     table_id = request.GET.get('table_id')

#     if not date_str or not table_id:
#         return JsonResponse({'times': []})

#     try:
#         date = datetime.strptime(date_str, '%Y-%m-%d').date()
#     except ValueError:
#         return JsonResponse({'times': []})

#     try:
#         # Ensure the table_id exists in your Table model
#         Table.objects.get(id=table_id)
#     except ObjectDoesNotExist:
#         return JsonResponse({'times': []})

#     # Filter reservations by both date and table_id
#     booked_times = Reservation.objects.filter(reservation_date=date, table_id=table_id).values_list('reservation_time', flat=True)
    
#     all_times = ['13:00', '14:00', '15:00', '16:00','17:30','18:00','18:30', '19:00', '19:30', '20:00','21:00','22:30']  # Replace with your actual time slots
#     available_times = [time for time in all_times if time not in booked_times]
    
#     return JsonResponse({'times': available_times})

@login_required
def view_profile(request):
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'resto/profile.html', context)



####################################################           LOGIN VIEW     ####################################################
class LoginView(View):
    def get(self, request):
        return render(request, 'registration/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home page or any other page
        else:
            return render(request, 'registration/login.html', {'error': 'Invalid username or password'})

class AdminMenuView(ListView):
    model = Section
    template_name = 'resto/admin_menu.html'
    context_object_name = 'sections'

    def get_queryset(self):
        return Section.objects.prefetch_related('menu_items').all()

class ReadStoriesView(TemplateView):
    template_name = 'resto/read_stories.html'

class MenuSearchView(ListView):
    template_name = 'resto/menu_search_results.html'
    context_object_name = 'menu_items'

    def get_queryset(self):
        query = self.request.GET.get('q')
        return MenuItem.objects.filter(name__icontains=query)

class RecommendationsView(View):
    def get(self, request, *args, **kwargs):
        
        # Retrieve recommended items (customize this logic based on your recommendation approach)
        user_item_matrix = pd.read_pickle('resto/user_item_matrix.pkl')
        item_similarity_df = pd.read_pickle('resto/item_similarity_df.pkl')
        

        # Generate recommendations for the user
        recommendations = get_recommendations(request.user.id, user_item_matrix, item_similarity_df)
        recommended_menu_items = MenuItem.objects.filter(id__in=recommendations)
        return render(request, 'resto/recommendations.html', {'recommendations':recommended_menu_items})
    def get_recommendations(user_id, user_item_matrix, item_similarity_df, num_recommendations=5):
    # Fetch user's order history
        user_orders = user_item_matrix.loc[user_id]
    
    # Calculate the scores for items based on similarity to user's ordered items
        scores = item_similarity_df.dot(user_orders).div(item_similarity_df.sum(axis=1))
    
    # Exclude items already ordered by the user
        ordered_items = user_orders[user_orders > 0].index.tolist()
        scores = scores.drop(ordered_items)
    
    # Get the top recommendations
        recommendations = scores.nlargest(num_recommendations).index.tolist()
    
        return recommendations
        
        # Render the recommendations.html template with recommendations context

class RedeemGiftView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        

        # Calculate total coins by summing earnings and subtracting redemptions
        earned_transactions = CoinTransaction.objects.filter(user=user, transaction_type='earn')
        redeemed_transactions = CoinTransaction.objects.filter(user=user, transaction_type='redeem')

        total_earned = sum(transaction.amount for transaction in earned_transactions)
        total_redeemed = sum(transaction.amount for transaction in redeemed_transactions)

        total_coins = total_earned + total_redeemed

        if total_coins >= 50 :
            # Deduct coins for reward
            # CoinTransaction.objects.create(user=user, amount=-50, transaction_type='redeem')
            # redeem_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            # messages.success(request, "Congratulations! You've redeemed 50 coins for a free gift.")
            return render(request, 'resto/redeem_gift_page.html' )
        else:
            messages.warning(request, "You do not have enough coins to redeem a gift yet.")
            return redirect('customer_dashboard')
        

class ConfirmRedeemGiftView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        earned_transactions = CoinTransaction.objects.filter(user=user, transaction_type='earn')
        redeemed_transactions = CoinTransaction.objects.filter(user=user, transaction_type='redeem')

        total_earned = sum(transaction.amount for transaction in earned_transactions)
        total_redeemed = sum(transaction.amount for transaction in redeemed_transactions)

        total_coins = total_earned + total_redeemed

        if total_coins >= 50:
            # Deduct coins for reward
            CoinTransaction.objects.create(user=user, amount=-50, transaction_type='redeem')

            # Generate a random redeem code
            redeem_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

            # messages.success(request, "Congratulations! You've redeemed 50 coins for a free gift.")
            return render(request, 'resto/freegift.html', {'redeem_code': redeem_code})
        else:
            messages.warning(request, "You do not have enough coins to redeem a gift yet.")
            return redirect('customer_dashboard')




####################################   AI PART ####################################################################################




# import joblib
# def predict_demand(request):
#     if request.method == 'POST':
#         # Get input data
#         menu_item = request.POST.get('menu_item')
#         day_of_week = pd.to_datetime(request.POST.get('date')).dayofweek
#         month = pd.to_datetime(request.POST.get('date')).month
#         year = pd.to_datetime(request.POST.get('date')).year

#         input_data = {
#             'day_of_week': day_of_week,
#             'month': month,
#             'year': year,
#             'menu_item': menu_item,
#         }
#         input_df = pd.DataFrame([input_data])
#         input_df = pd.get_dummies(input_df)
        
#         # Ensure all expected columns are present
#         model_columns = joblib.load('restaurant_model_columns.pkl')
#         for col in model_columns:
#             if col not in input_df.columns:
#                 input_df[col] = 0

#         # Load model
#         model = joblib.load('restaurant_model.pkl')
        
#         # Make prediction
#         prediction = model.predict(input_df)
        
#         return render(request, 'resto/predict_result.html', {'prediction': prediction[0]})
    
#     return render(request, 'resto/predict_form.html')




class PredictView(View):
    
    def get(self, request, *args, **kwargs):
        form = PredictionForm()
        return render(request, 'resto/prediction_form.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = PredictionForm(request.POST)
        if form.is_valid():
            data = {
                'day_of_week': [int(form.cleaned_data['day_of_week'])],
                'month': [int(form.cleaned_data['month'])],
                'year': [int(form.cleaned_data['year'])],
                'menu_item': [form.cleaned_data['menu_item']]
            }
            
            model = joblib.load('restaurant_model.pkl')
            model_columns = joblib.load('restaurant_model_columns.pkl')
            
            df = pd.DataFrame(data)
            df = pd.get_dummies(df, columns=['menu_item'])
            df = df.reindex(columns=model_columns, fill_value=0)
            
            prediction = round(model.predict(df)[0],2)
            
            context = {
                'prediction': prediction,
                'menu_item': form.cleaned_data['menu_item']
            }
            return render(request, 'resto/prediction_result.html', context)
        return render(request, 'resto/prediction_form.html', {'form': form})

import numpy as np 

kmeans = joblib.load('customer_segmentation_model.pkl')
scaler = joblib.load('customer_data_scaler.pkl')

def recommend_promotion(cluster_id):
    if cluster_id == 0:
        return "20% off your next order!"
    elif cluster_id == 1:
        return "Buy one get one free on selected items!"
    elif cluster_id == 2:
        return "Free dessert with any main course!"
    else:
        return "10% off your total bill!"

def get_user_stats(customer):
    orders = Order.objects.filter(customer=customer)
    total_quantity = sum(item.quantity for order in orders for item in order.order_items.all())
            
            # Calculate total spent
    total_spent = sum(item.quantity * item.menu_item.price for order in orders for item in order.order_items.all())
    order_count = orders.count()
    return total_quantity, total_spent, order_count

def get_recommendationss(request, user_id):
    customer = get_object_or_404(User, id=user_id)
    total_quantity, total_spent, order_count = get_user_stats(customer)
    user_data = np.array([[total_quantity, total_spent, order_count]])
    user_data_scaled = scaler.transform(user_data)
    cluster_id = kmeans.predict(user_data_scaled)[0]
    promotion = recommend_promotion(cluster_id)
    return render(request, 'resto/segment.html', {'promotion': promotion, 'user': customer})