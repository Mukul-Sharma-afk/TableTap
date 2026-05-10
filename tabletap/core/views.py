from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_backends
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now, localtime
from django.db.models import Sum
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
import json

from .forms import UserRegisterForm, BusinessForm, TableForm, MenuForm, MenuItemForm, MenuCategoryForm, CompleteRegistrationForm
from .models import Business, BusinessStaff, User, Table, Menu, MenuItem, MenuCategory, Order, OrderItem
from .utils import generate_qr_code

from django.core.paginator import Paginator

from django.urls import reverse

def landing_page(request):
    return render(request, 'core/landing.html')

def signup_view(request):

    # Created a multi-step signup form (Inspired by Ref. 2), and set the default step as 1 to start.
    
    step = 1
    business_list = Business.objects.all() # Used to get all the business for the dropdown if role != "owner"

    if request.method == 'POST':

        # Getting the form data for the user and business forms during signup.

        user_form = UserRegisterForm(request.POST)
        business_form = BusinessForm(request.POST)

        # There are two important checks here - One, if the user is an owner then the business form they filled must be valid.
        # Two, if the user != owner then they must be linked to a business that already exists.

        if user_form.is_valid() and ((user_form.cleaned_data['role'] == 'owner' and business_form.is_valid()) or (user_form.cleaned_data['role'] in ['staff', 'manager'] and request.POST.get('business_id'))):
            try:
                user = user_form.save(commit=False)
                user.first_name = user_form.cleaned_data.get('first_name')
                user.last_name = user_form.cleaned_data.get('last_name')
                user.save()

                role = user_form.cleaned_data['role']

                if role == 'owner':

                    #If the user is an owner then add a new business for the owner.

                    business = business_form.save(commit=False)
                    business.user = user
                    business.table_count = 0 # default 0 tables because we are allowing users to add tables later.
                    business.save()
                    BusinessStaff.objects.create(user=user, business=business, role='owner')
                else:

                    #If the user is not an owner then find the existing business using the id and create a business staff entry to link the user to the business.

                    business_id = request.POST.get('business_id')
                    if business_id:
                        business = Business.objects.get(id=business_id)
                        BusinessStaff.objects.create(user=user, business=business, role=role)
                    else:
                        messages.error(request, 'Please select a business.')
                        step = 3
                        return render(request, 'core/signup.html', {
                            'user_form': user_form,
                            'business_form': business_form,
                            'step': step,
                            'business_list': business_list,
                        })

                # Manually setting the auth backend and logs in the user (Ack: ChatGPT used to figure out why after adding social login, normal signup threw errors.)

                user.backend = get_backends()[0].__module__ + "." + get_backends()[0].__class__.__name__
                login(request, user)

                return redirect('dashboard')

            except Exception as e:
                messages.error(request, f"Error: {e}")
                step = 3

        else:

            # If form details were invalid then go back to the steps where it was invalid

            if user_form.data.get('first_name') or user_form.data.get('last_name'):
                step = 2
            if business_form.data.get('name') or request.POST.get('business_id'):
                step = 3

    else:
        user_form = UserRegisterForm()
        business_form = BusinessForm()

    return render(request, 'core/signup.html', {
        'user_form': user_form,
        'business_form': business_form,
        'step': step,
        'business_list': business_list,
    })

@csrf_exempt
@require_POST
def validate_signup_step1(request):
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()

        errors = []

        # Add errors to the list if the username or email is blank or already taken/ being used.

        if not username:
            errors.append("Username is required.")
        elif User.objects.filter(username=username).exists():
            errors.append("Username is already taken.")

        if not email:
            errors.append("Email is required.")
        elif User.objects.filter(email=email).exists():
            errors.append("Email is already in use.")

        return JsonResponse({
            'valid': len(errors) == 0,
            'errors': errors
        })

    except Exception as e:
        return JsonResponse({'valid': False, 'errors': [str(e)]})



def login_view(request):
    if request.method == 'POST':

        # After the form is submitted, gets the username and password and then checks if the creds are correct using authenticate.

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # If user is an admin then return to the landing page (Now with admin panel link in navbar)

            if user.role == 'admin':
                return redirect('landing')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials.')

    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def complete_registration_view(request):

    # Complete reg form made for users who use social login so that they can fill role and business details.
    
    user = request.user

    # If user is already in DB then redirect them to the dashboard, else make them fill in role and subsequent business details.

    if BusinessStaff.objects.filter(user=user).exists():
        return redirect('dashboard')

    # If user is not already registered in the DB then add their user and business details using form data.

    if request.method == 'POST':
        form = CompleteRegistrationForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.role = form.cleaned_data['role']
            user.save()

            role = form.cleaned_data['role']
            if role == 'owner':
                business = Business.objects.create(
                    user=user,
                    name=form.cleaned_data['business_name'],
                    business_type=form.cleaned_data['business_type'],
                    address=form.cleaned_data['address'],
                    phone_no=form.cleaned_data['phone_no'],
                    table_count=0
                )
            else:
                business = form.cleaned_data['business_id']

            BusinessStaff.objects.create(user=user, business=business, role=role)
            messages.success(request, "Registration completed successfully.")
            return redirect('dashboard')
    else:
        form = CompleteRegistrationForm()
        
    return render(request, 'core/complete_registration.html', {
        'form': form
    })

    return render(request, 'core/complete_registration.html', {'form': form})

@login_required
def dashboard_view(request):

    # If users are using social login and they are not linked to a business, then redirect to complete registration page.

    if request.session.pop('social_signup', False) or not BusinessStaff.objects.filter(user=request.user).exists():
        return redirect('complete_registration')

    user = request.user
    business_name = None
    try:
        business = Business.objects.get(businessstaff__user=user)
        business_name = business.name
    except Business.DoesNotExist:
        return redirect('login')

    # Below code gets all the details for the dashboard

    total_orders = Order.objects.filter(table__business=business).count()
    todays_orders = Order.objects.filter(table__business=business, created_at__date=now().date()).count()
    orders = Order.objects.filter(table__business=business)
    total_revenue = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
    avg_order_value = round(total_revenue / total_orders, 2) if total_orders > 0 else 0
    table_count = Table.objects.filter(business=business).count()
    recent_orders = orders.order_by('-created_at')[:5]

    return render(request, 'core/dashboard.html', {
        'user': user,
        'total_orders': total_orders,
        'todays_orders': todays_orders,
        'avg_order_value': avg_order_value,
        'table_count': table_count,
        'recent_orders': recent_orders,
        'business_name': business_name,
    })



@login_required
def table_management(request):
    user = request.user
    business_name = None

    # The below code was used when admins could also get into the dashboard (See design doc html mockups)
    # Since admins do not have businesses, they should not be able to access table, menu, or order management pages.

    try:
        business = Business.objects.get(businessstaff__user=request.user)
        business_name = business.name
    except Business.DoesNotExist:
        return redirect('dashboard')

    tables = Table.objects.filter(business=business)
    qr_count = tables.exclude(qr_code='').exclude(qr_code=None).count()

    # Add new table and generate QR code on the fly for the table.

    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            table = form.save(commit=False)
            table.business = business
            table.save()
            generate_qr_code(table)
            return redirect('table_management')
    else:
        form = TableForm()

    return render(request, 'core/table_management.html', {
        'form': form,
        'tables': tables,
        'qr_count': qr_count,
        'business_name': business_name,
    })

@login_required
def delete_table(request, table_id):
    table = get_object_or_404(Table, id=table_id)

    # Protective code to ensure that only users linked to a particular business can delete a table in the business.
    
    if not BusinessStaff.objects.filter(user=request.user, business=table.business).exists():
        messages.error(request, "You do not have permission to delete this table.")
        return redirect('table_management')

    table.delete()
    messages.success(request, f"Table {table.table_no} deleted successfully.")
    return redirect('table_management')

# View for the page that the customer can access when QR code is scanned at a table

def customer_menu(request, table_id):
    try:
        table = Table.objects.get(id=table_id)
        business = table.business
    except Table.DoesNotExist:
        return render(request, 'core/not_found.html', status=404)

    # Retrieve all Menus with is_enabled flag = True

    enabled_menus = Menu.objects.filter(business=business, is_enabled=True)

    # Retrieve all Categpries for Menus with is_enabled flag = True
    categories = MenuCategory.objects.filter(menu__in=enabled_menus).distinct()
    
    menu_data = []
    for category in categories:

        # Add all Menu Items that are available into the list and display those items for the customer.

        items = MenuItem.objects.filter(menu=category.menu, category=category, is_available=True)
        if items.exists():
            menu_data.append({
                'category': category.name,
                'items': items
            })

    return render(request, 'core/customer_menu.html', {
        'table': table,
        'business': business,
        'menu_data': menu_data
    })


@login_required
def order_management(request):
    user = request.user
    business = Business.objects.get(businessstaff__user=user)
    business_name = business.name
    status_filter = request.GET.get('status')

    # Page number added for pagination.
    page_number = request.GET.get('page')

    # Retrieves all the orders sorted by newest first
    orders = Order.objects.filter(table__business=business).order_by('-created_at')

    # Used to filter by status -> Eg. Select Pending to see all pending orders.
    if status_filter:
        orders = orders.filter(status=status_filter)

    # Limit orders to 5 per page.
    paginator = Paginator(orders, 5)
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/order_management.html', {
        'orders': orders,
        'selected_status': status_filter,
        'page_obj': page_obj,
        'business_name':business_name,
    })

@require_http_methods(["GET", "POST"])
@csrf_exempt
def order_detail_api(request, order_id):

    # Retrieve order details. If order does not exist then return 404 error as JSON.
    try:
        order = Order.objects.select_related('table').get(pk=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

    if request.method == 'GET':
        items = [
            {
                'name': item.menu_item.name,
                'quantity': item.quantity,
                'price': float(item.item_price)
            }
            for item in OrderItem.objects.filter(order=order).select_related('menu_item')
        ]

        return JsonResponse({
            'id': order.id,
            'table_no': order.table.table_no,
            'total_price': float(order.total_price),
            'status': order.status,
            'created_at': localtime(order.created_at).strftime('%B %d, %Y, %I:%M %p'),
            'items': items
        })

    # Allows staff and owners to process the orders by updaing the status.

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            if new_status in ['pending', 'in-progress', 'completed']:
                order.status = new_status
                order.save()
                return JsonResponse({'message': 'Order status updated successfully'})
            else:
                return JsonResponse({'error': 'Invalid status'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

@require_POST
@login_required
def update_order_status(request):
    order_id = request.POST.get('order_id')
    new_status = request.POST.get('status')
    try:
        order = Order.objects.get(id=order_id)
        if order.table.business.user == request.user or BusinessStaff.objects.filter(user=request.user, business=order.table.business).exists():
            order.status = new_status
            order.save()

            table = order.table
            has_active_orders = Order.objects.filter(table=table).exclude(status='completed').exists()

            if not has_active_orders:
                table.status = 'inactive'
                table.save()
                
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")

    # HTTP_REFERER used to take the user back to the previous page URL. (Ack: ChatGPT used to understand how referers work)
    referer = request.META.get('HTTP_REFERER', '/')
    return redirect(referer)


@login_required
def menu_management(request):
    user = request.user
    business_name = None

    try:
        business = Business.objects.get(businessstaff__user=user)
        business_name = business.name
    except Business.DoesNotExist:
        return redirect('dashboard')

    menus = Menu.objects.filter(business=business)
    menu_id = request.GET.get('menu_id')

    if menu_id:
        menu = get_object_or_404(Menu, id=menu_id, business=business)
    else:
        menu = menus.first()  # fallback to first menu

    menu_items = MenuItem.objects.filter(menu=menu) if menu else []
    categories = MenuCategory.objects.filter(menu=menu) if menu else []

    return render(request, 'core/menu_management.html', {
        'menus': menus,
        'selected_menu': menu,
        'menu_items': menu_items,
        'categories': categories,
        'business_name': business_name,
    })

@login_required
def menu_add(request):
    user = request.user
    try:
        business = Business.objects.get(businessstaff__user=user)
    except Business.DoesNotExist:
        return redirect('dashboard')

    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            menu = form.save(commit=False)
            menu.business = business
            menu.save()
            return redirect('menu_management')
    else:
        form = MenuForm()

    return render(request, 'core/menu_add.html', {'form': form})

@login_required
def menu_edit(request, menu_id):
    menu = get_object_or_404(Menu, id=menu_id)

    if not BusinessStaff.objects.filter(user=request.user, business=menu.business).exists():
        return HttpResponseForbidden("You do not have permission to edit this menu.")

    if request.method == 'POST':
        form = MenuForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('menu_management')}?menu_id={menu.id}")
    else:
        form = MenuForm(instance=menu)

    return render(request, 'core/menu_edit.html', {
        'form': form,
        'title': 'Edit Menu',
        'menu_id': menu.id
    })

@login_required
def menu_delete(request, menu_id):
    menu = get_object_or_404(Menu, id=menu_id)
    user = request.user
    business = Business.objects.get(businessstaff__user=user)

    if request.method == 'POST':
        menu.delete()
        return redirect('menu_management')

    return render(request, 'core/confirm_delete.html', {
        'object': menu,
        'title': 'Delete Menu',
        'message': f'Are you sure you want to delete the menu "{menu.name}"?',
        'action_url': request.path,
    })

@login_required
@require_POST
def menu_toggle(request, menu_id):
    user = request.user
    business = Business.objects.get(businessstaff__user=user)
    menu = get_object_or_404(Menu, id=menu_id, business=business)
    
    menu.is_enabled = not menu.is_enabled
    menu.save()

    # Toggle enable/ disable for the menu and then return to the menu management page with the same menu selected.
    
    return redirect(f"{reverse('menu_management')}?menu_id={menu.id}")

@login_required
def menu_item_add(request):
    user = request.user
    menu_id = request.GET.get('menu')

    business = Business.objects.get(businessstaff__user=user)

    try:
        business = Business.objects.get(businessstaff__user=user)
        if not menu_id:
            return HttpResponseBadRequest("No menu selected.")

        menu = Menu.objects.get(id=menu_id, business=business)
    except Business.DoesNotExist:
        return HttpResponseBadRequest("Business not found.")
    except Menu.DoesNotExist:
        return HttpResponseForbidden("Menu not found or does not belong to your business.")

    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, business=business)
        if form.is_valid():
            item = form.save(commit=False)
            item.menu = menu
            item.save()
            return redirect(f'{reverse("menu_management")}?menu_id={item.menu.id}')
    else:
        form = MenuItemForm(business=business)

    return render(request, 'core/menu_item_add.html', {
        'form': form,
        'title': 'Add Menu Item',
        'menu_id': menu.id,
    })


@login_required
def menu_item_edit(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    user = request.user

    if item.menu.business != Business.objects.get(businessstaff__user=user):
        return HttpResponseForbidden("You do not have access to this item.")
        
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=item, business=item.menu.business)

        if form.is_valid():
            form.save()
            # return redirect('menu_management')
            return redirect(f'{reverse("menu_management")}?menu_id={item.menu.id}')
    else:
        form = MenuItemForm(instance=item, business=item.menu.business)


    return render(request, 'core/menu_item_form.html', {'form': form, 'title': 'Edit Menu Item'})

@login_required
def menu_item_delete(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    item.delete()
    # return redirect('menu_management')
    return redirect(f'{reverse("menu_management")}?menu_id={item.menu.id}')

@login_required
@require_POST
def menu_item_toggle(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    user = request.user

    if item.menu.business != Business.objects.get(businessstaff__user=user):
        return HttpResponseForbidden("You do not have access to this item.")

    item.is_available = not item.is_available
    item.save()
    return redirect(f'{reverse("menu_management")}?menu_id={item.menu.id}')

@login_required
def menu_category_add(request):
    user = request.user
    business = Business.objects.get(businessstaff__user=user)

    # Get menu ID from the URL
    menu_id = request.GET.get('menu')
    if not menu_id:
        return HttpResponseBadRequest("No menu selected.")

    # Try to retrieve the selected menu
    try:
        menu = Menu.objects.get(id=menu_id, business=business)
    except Menu.DoesNotExist:
        return HttpResponseForbidden("Menu not found.")

    if request.method == 'POST':
        form = MenuCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.menu = menu
            category.save()
            return redirect(f'{reverse("menu_management")}?menu_id={menu.id}')
    else:
        form = MenuCategoryForm()

    return render(request, 'core/menu_category_form.html', {
        'form': form,
        'title': 'Add Category',
        'menu': menu
    })

@login_required
def menu_category_edit(request, category_id):
    category = get_object_or_404(MenuCategory, id=category_id)
    user = request.user
    business = Business.objects.get(businessstaff__user=user)

    if category.menu.business != business:
        return HttpResponseForbidden("You do not have access to this category.")

    if request.method == 'POST':
        form = MenuCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            # return redirect('menu_management')
            return redirect(f'{reverse("menu_management")}?menu_id={category.menu.id}')

    else:
        form = MenuCategoryForm(instance=category)

    return render(request, 'core/menu_category_form.html', {'form': form, 'title': 'Edit Category'})


@login_required
def menu_category_delete(request, category_id):
    category = get_object_or_404(MenuCategory, id=category_id)
    user = request.user
    business = Business.objects.get(businessstaff__user=user)

    if category.menu.business != business:
        return HttpResponseForbidden("You do not have access to this category.")

    category.delete()
    # return redirect('menu_management')
    return redirect(f'{reverse("menu_management")}?menu_id={category.menu.id}')


@csrf_exempt
def submit_order(request, table_id):

    # Taking the table id from the URL to know which table the customer is ordering from.

    if request.method == 'POST':
        try:
            table = Table.objects.get(id=table_id)
            business = table.business
            data = json.loads(request.body)

            if not data:
                return JsonResponse({'success': False, 'message': 'Empty cart'}, status=400)

            total_price = 0
            order_items = []

            for item_id, qty in data.items():
                menu_item = MenuItem.objects.get(id=item_id)
                item_total = menu_item.price * int(qty)
                total_price += item_total
                order_items.append((menu_item, qty, menu_item.price))

            order = Order.objects.create(
                table=table,
                total_price=total_price,
                status='pending'
            )

            table.status = 'active'
            table.save()

            for item, qty, price in order_items:
                OrderItem.objects.create(
                    order=order,
                    menu_item=item,
                    quantity=qty,
                    item_price=price
                )

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=405)