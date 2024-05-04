from api.bitrix import Bitrix
from api.models import Product, Category

from django.conf import settings

RESPONSIBLE = settings.BITRIX_USER_ID
IBLOCK_ID = settings.IBLOCK_ID

BITRIX = Bitrix()

def check_product(data: dict) -> bool:
	params = {
		"select": [
			"id",
			"iblockId",
			"*"
		],
		"filter": {
			"iblockId": IBLOCK_ID,
			"code": str(data.get("code"))
		},
		"order": {
			"id": "ASC"
		}
	}
	
	response = BITRIX.call("catalog.product.list", params)
	if 'result' not in response or 'products' not in response['result']:
		raise ValueError("Error while listing products: %s" % response['result'])

	if response['total'] != 1:
		return False
	
	response = response['result']['products'][0]
	if response['code'] == str(data['code']):
		return True
	return False

def set_price(price: int, product_id: int, currency: str = "UZS"):
	params = dict(
		fields=dict(
			catalogGroupId=1,
			currency=currency,
			price=price,
			productId=product_id
		)
	)
	
	response = BITRIX.call("catalog.price.add", params)
	if 'result' not in response or 'price' not in response['result']:
		raise ValueError("Error while creating product: %s" % response['result'])
	return response

def create_product(data: dict):
	params = dict(
		fields=dict(
			iblockId=IBLOCK_ID,
			iblockSectionId=data.get('iblockSectionId', None),
			name=data.get('name'),
			code=data.get('code'),
			xmlId=data.get('code'),
			detailText=data.get('description', None),
			createdBy=str(RESPONSIBLE)
		)
	)
	
	if 'property' in data:
		params['fields'][data['property']['key']] = {
			'value': data['property']['value']
		}
	
	response = BITRIX.call("catalog.product.add", params)
	if 'result' not in response or 'element' not in response['result']:
		raise ValueError("Error while creating product: %s" % response['result'])
	
	response = response['result']['element']
	
	product, created = Product.objects.get_or_create(
		bitrix_id = response['id'],
		code = response['code'],
		name = response['name'],
		description = response['detailText'],
		retail_price = data.get('price', 0)
	)
	
	if created:
		set_price(data['price'], response['id'])
		
		if not data['iblockSectionId']:
			return product

		category = Category.objects.get(bitrix_id=int(data['iblockSectionId']))
		product.category = category
		product.save()
	return product
