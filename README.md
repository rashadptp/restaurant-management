# Restaurant Management System
## Project Overview
The Restaurant Management System is a comprehensive web application designed to streamline the operations of a restaurant. The system allows customers to place orders, reserve tables, and manage their dining experience, while administrators can oversee orders, manage menus, and track revenue. The project is built using Django, a high-level Python web framework, and follows a modular and scalable architecture to ensure efficiency and ease of use.
![image](https://github.com/user-attachments/assets/2e7c5c16-0de4-4815-8e49-7a2d46bcaeff)
![image](https://github.com/user-attachments/assets/37c3efcc-c1e9-4f10-8f04-746ac1d74afc)
![image](https://github.com/user-attachments/assets/58fb103d-adf4-4ad5-81ed-b34b8ce50325)
![image](https://github.com/user-attachments/assets/3d57e940-456e-4800-a6d1-672203fca9de)


## Features
## Customer Dashboard
Profile Management: Customers can view and edit their profiles.
Order Placement: Customers can place orders by selecting menu items and assigning them to a table.
Table Reservations: Customers can reserve tables for their dining experience.
Order Tracking: Customers can view their active and completed orders.
Personalized Offers: The system provides personalized offers based on customer preferences.
## Admin Dashboard
Order Management: Admins can view and manage all orders, including their statuses (Processing, Delivered).
Revenue Tracking: The total revenue from delivered orders is displayed, allowing admins to track the financial performance.
Menu Management: Admins can manage the restaurant's menu, adding or removing items as needed.
Table Management: Admins can oversee table reservations and manage availability.
Order Management
Order Creation: Customers can create orders by selecting items from the menu and specifying quantities.
Total Amount Calculation: The system automatically calculates the total amount for each order based on the selected items and their quantities.
## Staff Dashboard
Order Status: Orders are tracked with statuses (Processing, Delivered), and admins can update these statuses as needed.
Technical Details
Models
User: Represents the customers and admins who interact with the system.
Order: Tracks customer orders, including items, table assignments, and status.
MenuItem: Represents individual items on the restaurant's menu.
Table: Represents the tables available for reservation in the restaurant.
OrderItem: A bridge between orders and menu items, tracking quantities and associations.
Views
PlaceOrderView: Allows customers to place orders, select items, and assign them to tables.
AdminDashboardView: Provides an overview of the restaurant's operations, including revenue and order counts.
OrderListView: Displays a list of orders, filtered by status, for both customers and admins.


Technologies Used
## Django: The core framework for building the application.

Bootstrap: For responsive and modern UI components.
POSTGRE SQL: Database management for storing all data.
Git/GitHub: Version control and collaboration.


## Installation
To run this project locally:

Clone the repository:


git clone https://github.com/your-username/restaurant-management-system.git
Navigate to the project directory:
bash

cd restaurant-management-system
Install the dependencies:


pip install -r requirements.txt
Apply the migrations:

python manage.py migrate
Run the development server:

python manage.py runserver
Contributing
Contributions are welcome! Please feel free to submit a Pull Request or raise an issue to suggest improvements or report bugs.

License
This project is licensed under the MIT License. See the LICENSE file for details.


https://github.com/user-attachments/assets/8945661b-16a6-46ad-a5e2-bd54ae877802


