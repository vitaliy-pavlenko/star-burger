import phonenumbers

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
    errors = []

    firstname_error = validate_string_field(order, 'firstname')
    if firstname_error:
        errors.append(firstname_error)

    lastname_error = validate_string_field(order, 'lastname')
    if lastname_error:
        errors.append(lastname_error)

    address_error = validate_string_field(order, 'address')
    if address_error:
        errors.append(address_error)

    phonenumber_error = validate_phonenumber_field(order, 'phonenumber')
    if phonenumber_error:
        errors.append(phonenumber_error)

    products_error = validate_order_items(order, 'products', Product)
    if products_error:
        errors.append(products_error)

    if errors:
        raise ValidationError(errors)


def validate_string_field(data, field_name):
    if field_name not in data:
        return f'{field_name}: Обязательное поле'
    else:
        field_data = data.get(field_name)
        if field_data is None:
            return f'{field_name}: Это поле не может быть пустым'
        if not isinstance(field_data, str):
            return f'{field_name}: Not a valid string'
    return None


def validate_phonenumber_field(data, field_name):
    if field_name not in data:
        return f'{field_name}: Обязательное поле'
    else:
        field_data = data.get(field_name)
        if not field_data or field_data is None:
            return f'{field_name}: Это поле не может быть пустым'
        if not phonenumbers.is_valid_number(phonenumbers.parse(field_data)):
            return f'{field_name}: Введен некорректный номер телефона'
    return None


def validate_order_items(data, field_name, model):
    if field_name not in data:
        return f'{field_name}: Обязательное поле'
    else:
        field_data = data.get(field_name)
        if field_data is None:
            return f'{field_name}: Это поле не может быть пустым'
        if isinstance(field_data, str):
            return f'{field_name}: Ожидался list со значениями, но был получен "str"'
        if isinstance(field_data, list) and len(field_name) < 1:
            return f'{field_name}: Этот список не может быть пустым'

        errors = []
        for item in field_data:
            pk = item.get(model.__name__.lower())
            try:
                model.objects.get(pk=pk)
            except Product.DoesNotExist:
                errors.append(f'{field_name}: Недопустимый первичный ключ {pk}')
        if errors:
            return errors

    return None
