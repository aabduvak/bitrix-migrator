from api.bitrix import Bitrix
from api.models import Product, Document, DocumentProduct

from django.conf import settings
from django.db.models import Sum

RESPONSIBLE = settings.BITRIX_USER_ID
BITRIX = Bitrix()

def create_document(data: dict) -> Document:
	params = {
		"fields": {
			"docType": data.get("doc_type", "A"),
			"responsibleId": int(RESPONSIBLE),
			"currency": data.get("currency", "UZS")
		}
	}
	
	response = BITRIX.call("catalog.document.add", params)
	if "result" not in response or "document" not in response["result"]:
		raise ValueError("Invalid response from Bitrix24: %s" % response)
	response = response["result"]["document"]
	
	doc = Document.objects.create(
		bitrix_id = response["id"],
		type=response["docType"],
		title=response["title"],
		status=response["status"],
		total=0,
		currency=response["currency"]
	)
	return doc

def set_supplier(id: int, supplier_id: int = 1, type_id: int = 4):
	params = dict(
		fields = dict(
			documentId=id,
			entityTypeId=type_id, # Company type
			entityId=supplier_id
		)
	)
	
	response = BITRIX.call("catalog.documentcontractor.add", params)
	return response

def conduct_document(id: int) -> bool:
	params = dict(
		id=id,
	)
	
	response = BITRIX.call("catalog.document.conduct", params)
	return response["result"]

def cancel_document(id: int) -> bool:
	params = dict(
		id=id,
	)
	
	response = BITRIX.call("catalog.document.cancel", params)
	return response["result"]

def update_document_total(id: int):
	total = 0
	
	queryset = DocumentProduct.objects.filter(document__bitrix_id=id)
	
	for instance in queryset:
		total += instance.amount * instance.purchase_price
	
	params = dict(
		id=id,
		fields = dict(
			total=str(total)
		)
	)
	
	response = BITRIX.call("catalog.document.update", params)
	return response

def add_item_document(document: Document, product: Product, data: dict) -> DocumentProduct:
	params = dict(
		fields = dict(
			docId=document.bitrix_id,
			elementId=product.bitrix_id,
			amount=data.get("amount"),
			purchasingPrice=data.get("purchase_price"),
			storeTo=1
		)
	)
	
	response = BITRIX.call("catalog.document.element.add", params)
	
	if 'result' not in response or 'documentElement' not in response['result']:
		raise ValueError("Could not add element to document: %s" % response['result'])
	
	elem = DocumentProduct.objects.create(
		product=product,
		document=document,
		purchase_price=data['purchase_price'],
		amount=data['amount'],
		bitrix_id=response['result']['documentElement']['id']
	)
	return elem

def delete_item_from_document(id: int):
	params = dict(
		id=id
	)
	
	response = BITRIX.call("catalog.document.element.delete", params)
	if 'result' not in response or not response['result']:
		raise ValueError("Couldn't delete position in document: %s" % response)
	
	DocumentProduct.objects.get(bitrix_id=id).delete()
	return response

def delete_invalid_items():
	queryset = DocumentProduct.objects.filter(amount__lte=0)
	
	for item in queryset:
		delete_item_from_document(item.bitrix_id)
	
	return