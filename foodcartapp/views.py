from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Order, OrderItem, Product


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    try:
        validate_order(request.data)
        new_order = Order.objects.create(
            firstname=request.data.get('firstname'),
            lastname=request.data.get('lastname'),
            phonenumber=request.data.get('phonenumber'),
            address=request.data.get('address'),
        )
        order_items = request.data.get('products')
        for item in order_items:
            OrderItem.objects.create(
                order=new_order,
                product=Product.objects.get(pk=item.get('product')),
                quantity=item.get('quantity'),
            )
    except ValueError as e:
        return Response({
            'error': f'Something went wrong - {e}',
        })
    return Response({})


def validate_order(order):
    if 'products' not in order:
        raise ValidationError('products: Обязательное поле')

    order_items = order.get('products')

    if order_items is None:
        raise ValidationError('products: Это поле не может быть пустым')

    if isinstance(order_items, str):
        raise ValidationError('products: Ожидался list со значениями, но был получен "str"')

    if isinstance(order_items, list) and len(order_items) < 1:
        raise ValidationError('products: Этот список не может быть пустым')
