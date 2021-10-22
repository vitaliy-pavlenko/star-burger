import json

from django.http import JsonResponse
from django.templatetags.static import static


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


def register_order(request):
    try:
        request_data = json.loads(request.body.decode())
        new_order = Order.objects.create(
            firstname=request_data.get('firstname'),
            lastname=request_data.get('lastname'),
            phonenumber=request_data.get('phonenumber'),
            address=request_data.get('address'),
        )
        order_items = request_data.get('products')
        for item in order_items:
            OrderItem.objects.create(
                order=new_order,
                product=Product.objects.get(pk=item.get('product')),
                quantity=item.get('quantity'),
            )
    except ValueError as e:
        return JsonResponse({
            'error': f'Something went wrong - {e}',
        })
    return JsonResponse({})
