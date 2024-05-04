import pandas as pd
from django.conf import settings

from api.bitrix import Bitrix
from api.utils.document import (
    create_document,
    set_supplier,
    add_item_document,
    conduct_document,
    update_document_total,
)
from api.utils.product import check_product, create_product
from api.utils.section import check_section, create_section
from api.models import Product, Category, Document

RESPONSIBLE = settings.BITRIX_USER_ID
BITRIX = Bitrix()


def handle_file(file: str) -> list[dict]:
    df = pd.read_excel(file)
    rows = []

    for index, row in df.iterrows():
        rows.append(row.to_dict())
    return rows


def process_data(product_list: list[dict], **kwargs):
    doc = create_document({"doc_type": "A", "currency": "UZS"})

    print("document created: {id}".format(id=doc.id))

    set_supplier(doc.bitrix_id, kwargs.get("supplier_id", 1))

    for product in product_list:
        if not check_product(product):
            if not check_section(product["category"]):
                create_section(product["category"])

            category = Category.objects.get(name=product["category"])
            product["iblockSectionId"] = category.bitrix_id
            product["property"] = {
                "value": product["code"],
                "key": kwargs.get("property", "property109"),
            }
            create_product(product)

        prod = Product.objects.get(code=product["code"])
        add_item_document(doc, prod, product)
        print("product added to document: {id}".format(id=prod.id))

    update_document_total(doc.bitrix_id)
    conduct_document(doc.bitrix_id)
    print("document conducted: {id}".format(id=doc.id))
