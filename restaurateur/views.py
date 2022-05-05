from django import forms
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from geopy.distance import distance

from foodcartapp.models import Product, Restaurant, Order
from place.crud_helpers import get_places


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def enrich_orders_with_delivery_distance(orders):
    order_addresses = [o.address for o in orders]
    restaurants = Restaurant.objects.all()
    restaurants_addresses = [r.address for r in restaurants]
    places = get_places(order_addresses + restaurants_addresses)
    for order in orders:
        order_place = places.get(order.address)

        for restaurant in order.restaurants:
            restaurant_place = places.get(restaurant.address)
            restaurant.distance = calculate_distance(order_place, restaurant_place)

        order.restaurants.sort(key=lambda r: r.distance)


def calculate_distance(one_place, another_place):
    return round(distance(
        (one_place.longitude, one_place.latitude),
        (another_place.longitude, another_place.latitude)
    ).km, 3)


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.filter(status=Order.NEW)\
        .annotate(total_count=Sum('items__total_price'))\
        .fetch_available_restaurants()

    enrich_orders_with_delivery_distance(orders)

    return render(request, template_name='order_items.html', context={
        'order_items': orders,
    })
