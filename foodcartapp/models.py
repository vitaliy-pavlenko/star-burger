from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Count
from django.utils import timezone
from geopy.distance import distance
from phonenumber_field.modelfields import PhoneNumberField

from restaurateur.utils import get_coordinates


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50,
        db_index=True
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def fetch_available_restaurants(self):
        for order in self:
            order_coords = get_coordinates(order.address)
            available_restaurants_qs = RestaurantMenuItem.objects.filter(
                availability=True, product_id__in=order.items.values_list('product_id', flat=True)
            )\
                .values('restaurant_id')\
                .order_by('restaurant_id')\
                .annotate(available_restaurants_count=Count('restaurant_id'))\
                .filter(available_restaurants_count=order.items.count())

            order.restaurants = []
            restaurants = Restaurant.objects.filter(id__in=available_restaurants_qs.values_list('restaurant_id', flat=True))

            for restaurant in restaurants:
                restaurant_coords = get_coordinates(restaurant.address)
                restaurant.distance = round(distance(order_coords, restaurant_coords).km, 3)
                order.restaurants.append(restaurant)

            order.restaurants.sort(key=lambda r: r.distance)

        return self


class Order(models.Model):
    NEW = 1
    PROCESSING = 2
    DELIVERING = 3
    DONE = 4
    STATUS_CHOICES = (
        (NEW, 'Необработанный'),
        (PROCESSING, 'Обрабатывается'),
        (DELIVERING, 'В доставке'),
        (DONE, 'Выполнен'),
    )
    CASH = 1
    CARD = 2
    PAYMENT_METHOD_CHOICES = (
        (CASH, 'Оплата наличными'),
        (CARD, 'Оплата картой')
    )
    firstname = models.CharField(max_length=100, verbose_name='Имя')
    lastname = models.CharField(max_length=100, verbose_name='Фамилия')
    phonenumber = PhoneNumberField(max_length=15, verbose_name='Телефон')
    address = models.CharField(max_length=200, verbose_name='Адрес')
    status = models.IntegerField(choices=STATUS_CHOICES, default=NEW, verbose_name='Статус', db_index=True)
    comment = models.TextField(max_length=300, blank=True, verbose_name='Комментарий к заказу')
    registered_at = models.DateTimeField(default=timezone.now, verbose_name='Время регистрации заказа', db_index=True)
    called_at = models.DateTimeField(null=True, blank=True, verbose_name='Время звонка менеджера', db_index=True)
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='Время доставки', db_index=True)
    payment_method = models.IntegerField(choices=PAYMENT_METHOD_CHOICES, verbose_name='Способ оплаты', null=True, db_index=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name='Ресторан')

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.address}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, related_name='items', verbose_name='Товар')
    quantity = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    total_price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Стоимость товара')

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f'{self.product.name} {self.order}'
