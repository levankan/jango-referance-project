from django.db import models

class Shipment(models.Model):
    serial_lot = models.CharField(max_length=255, default="default_value")  # Matches 'Serial/Lot'
    document_number = models.CharField(max_length=255)  # Matches 'Document Number'
    item_number = models.CharField(max_length=255)  # Matches 'Item Number'
    cross_reference = models.CharField(max_length=255)  # Matches 'Cross Reference'
    qty = models.CharField(max_length=255)  # Matches 'QTY'
    box = models.CharField(max_length=255)  # Matches 'Box'
    invoice = models.CharField(max_length=255)  # Matches 'Invoice'
    invoice_date = models.CharField(max_length=255)  # Matches 'Invoice Date'
    packing_list = models.CharField(max_length=255)  # Matches 'Packing List'
    description = models.CharField(max_length=255)  # Matches 'Description'
    qarbon_qty = models.CharField(max_length=255)  # Matches 'Qarbon Qty'
    lot_carbon = models.CharField(max_length=255)  # Matches 'Lot Carbon'
    pallet = models.CharField(max_length=255)  # Matches 'Pallet'
    

    def __str__(self):
        return self.Serial_Lot







class PalletDimension(models.Model):
    """
    Stores dimension data for each numeric pallet number.
    The field pallet_number can be a CharField or IntegerField,
    depending on your use case.
    """
    pallet_number = models.CharField(max_length=10, default='Unknown')
    length_cm = models.PositiveIntegerField(null=True, blank=True)
    width_cm = models.PositiveIntegerField(null=True, blank=True)
    height_cm = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Pallet {self.pallet_number}: {self.length_cm} X {self.width_cm} X {self.height_cm} cm"
