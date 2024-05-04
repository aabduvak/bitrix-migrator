import uuid

from django.db import models
from django.contrib.auth.models import User


class GetOrNoneManager(models.Manager):
    """Adds get_or_none method to objects"""

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True)
    created_by = models.ForeignKey(
        User,
        models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_%(model_name)ss",
        editable=False,
    )
    updated_by = models.ForeignKey(
        User,
        models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_%(model_name)ss",
        editable=False,
    )

    objects = GetOrNoneManager()

    class Meta:
        abstract = True
        ordering = ("id",)


class Document(BaseModel):
    DOC_TYPE_CHOICES = (
        (
            "A",
            "Приход товара на склад",
        ),
        (
            "S",
            "Оприходование товара",
        ),
        (
            "M",
            "Перемещение товара между складами",
        ),
        (
            "R",
            "Возврат товара",
        ),
        (
            "D",
            "Списание товара",
        ),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, null=True, blank=True)
    type = models.CharField(
        max_length=100, null=True, blank=True, choices=DOC_TYPE_CHOICES
    )
    currency = models.CharField(max_length=10, default="UZS")
    bitrix_id = models.IntegerField()
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=100, null=True, blank=True)


class Category(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=200, blank=True, null=True)
    name = models.CharField(max_length=200)
    bitrix_id = models.IntegerField()

    def __str__(self) -> str:
        return self.name


class Product(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=100)
    currency = models.CharField(max_length=100, default="UZS")
    retail_price = models.DecimalField(max_digits=10, decimal_places=2)
    bitrix_id = models.IntegerField(null=True, blank=True)
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        related_name="products",
        on_delete=models.SET_NULL,
    )

    def __str__(self) -> str:
        return self.name


class DocumentProduct(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.IntegerField(default=0)
    bitrix_id = models.IntegerField(null=True, blank=True)
