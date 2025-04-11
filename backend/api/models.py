from django.db import models


class Product(models.Model):
    ozon_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    image_url = models.URLField(blank=True, null=True)
    last_page_id = models.CharField(max_length=255, blank=True, null=True)  # Новое поле

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Продукты'
        verbose_name_plural = 'Продукт'


class OzonApiKey(models.Model):
    name = models.CharField(max_length=255, unique=True)
    client_id = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ключи'
        verbose_name_plural = 'Ключ'