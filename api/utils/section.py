from api.bitrix import Bitrix
from api.models import Category

from django.conf import settings

RESPONSIBLE = settings.BITRIX_USER_ID
IBLOCK_ID = settings.IBLOCK_ID
BITRIX = Bitrix()


def check_section(section: str) -> bool:
    params = {"filter": {"iblockId": IBLOCK_ID}}

    response = BITRIX.call("catalog.section.list", params)
    if "result" not in response or "sections" not in response["result"]:
        raise ValueError("Error while listing sections: %s" % response["result"])

    response = response["result"]["sections"]
    for item in response:
        if str(item["name"]).strip().lower() == section.lower():
            return True
    return False


def create_section(section: str) -> Category:
    params = dict(
        fields=dict(
            iblockId=IBLOCK_ID,
            iblockSectionId=None,
            name=section.strip(),
            code=section.strip(),
        )
    )

    response = BITRIX.call("catalog.section.add", params)
    if "result" not in response or "section" not in response["result"]:
        raise ValueError("Error while creating section: %s" % response["result"])

    response = response["result"]["section"]

    category, _ = Category.objects.get_or_create(
        bitrix_id=response["id"],
        code=response["code"],
        name=response["name"],
    )
    return category
