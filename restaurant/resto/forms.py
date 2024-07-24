# resto/forms.py

from django import forms
from .models import Table,OrderItem,Order
from django.forms import inlineformset_factory
class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['number', 'seats']


from django import forms
from .models import Reservation, Table
from datetime import datetime

from django import forms
from .models import Reservation, Table

class ReservationForm(forms.ModelForm):
    reservation_start_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'}))
    reservation_end_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'}))

    class Meta:
        model = Reservation
        fields = ['reservation_date', 'reservation_start_time', 'reservation_end_time', 'table']
        widgets = {
            'reservation_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)
        self.fields['table'].queryset = Table.objects.all()

    # def get_available_times(self, date, table_id):
    #     booked_times = Reservation.objects.filter(reservation_date=date, table_id=table_id).values_list('reservation_time', flat=True)
    #     all_times = ['13:00', '14:00', '15:00', '16:00']  # Replace with your actual time slots
    #     available_times = [(time, time) for time in all_times if time not in booked_times]
    #     return available_times



   

###############################TO ADD FIRSTNAME AND LASTNAME########################
# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from .models import CustomUser  # Use your custom user model

# class CustomUserCreationForm(UserCreationForm):
#     first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
#     last_name = forms.CharField(max_length=30, required=True, help_text='Required.')

#     class Meta(UserCreationForm.Meta):
#         model = CustomUser
#         fields = UserCreationForm.Meta.fields + ('first_name', 'last_name')


from django import forms
from .models import OrderItem,MenuItem

# forms.py

from django import forms
from .models import Order, OrderItem, MenuItem

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['table']

from django import forms
from .models import OrderItem, MenuItem

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['menu_item', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Retrieve queryset of menu items
        menu_items = MenuItem.objects.all()
        
        # Prepare choices with additional data attributes
        choices = []
        for item in menu_items:
            choices.append((item.id, f"{item.name} (Rs.{item.price})"))

        # Update widget choices and data-price attribute
        self.fields['menu_item'].widget.choices = choices
        for item_id, label in choices:
            self.fields['menu_item'].widget.attrs.update({
                f'data-price-{item_id}': MenuItem.objects.get(id=item_id).price
            })

OrderItemFormSet = forms.inlineformset_factory(
    Order, OrderItem, form=OrderItemForm, extra=1, can_delete=True
)


# Define a formset for OrderItem
# OrderItemFormSet = inlineformset_factory(
#     Order,  # Parent model
#     OrderItem,  # Child model
#     fields=['menu_item', 'quantity'],  # Fields to include in the form
#     extra=1,  # Number of extra forms to display
#     can_delete=True  # Allow deletion of forms
# )



# forms.py

from django import forms
from datetime import datetime



DAYS_OF_WEEK = [
    (6, 'Sunday'),
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
]

class PredictionForm(forms.Form):
    day_of_week = forms.ChoiceField(
        choices=DAYS_OF_WEEK,
        label="Day of the Week"
    )
    month = forms.ChoiceField(
        choices=[(i, datetime.strptime(str(i), "%m").strftime("%B")) for i in range(1, 13)],
        label="Month"
    )
    year = forms.IntegerField(
        initial=datetime.now().year,
        min_value=2020,  # Adjust as needed
        max_value=2100,  # Adjust as needed
        label="Year"
    )

    menu_item = forms.ChoiceField(
        choices=[],
        label="Menu Item"
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate menu_item choices dynamically
        menu_items = MenuItem.objects.all()
        self.fields['menu_item'].choices = [(item.name, item.name) for item in menu_items]