# views.py

import pandas as pd
from django.shortcuts import render
from .forms import ExcelUploadForm
from .models import Shipment

def shipments(request):
    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                # Read the Excel file using pandas
                df = pd.read_excel(file)

                # Rename columns to match model field names
                df.rename(columns={  
                    'Serial/Lot': 'serial_lot',
                    'Document Number': 'document_number',
                    'Item Number': 'item_number',
                    'Cross Reference': 'cross_reference',
                    'QTY': 'qty',
                    'Box': 'box',
                    'Invoice': 'invoice',
                    'Invoice Date': 'invoice_date',
                    'Packing List': 'packing_list',
                    'Description': 'description',
                    'Qarbon Qty': 'qarbon_qty',
                    'Lot Carbon': 'lot_carbon',
                    'Pallet': 'pallet'
                }, inplace=True)

                # Save data to the database
                for _, row in df.iterrows():
                    Shipment.objects.create(
                        serial_lot=row['serial_lot'],
                        document_number=row['document_number'],
                        item_number=row['item_number'],
                        cross_reference=row['cross_reference'],
                        qty=row['qty'],
                        box=row['box'],
                        invoice=row['invoice'],
                        invoice_date=row['invoice_date'],
                        packing_list=row['packing_list'],
                        description=row['description'],
                        qarbon_qty=row['qarbon_qty'],
                        lot_carbon=row['lot_carbon'],
                        pallet=row['pallet']
                    )

                # Fetch all shipment records from the database
                shipments = Shipment.objects.all()

                return render(request, 'shipments/shipments.html', {'form': form, 'shipments': shipments, 'success': 'File uploaded and data saved successfully.'})
            except Exception as e:
                return render(request, 'shipments/shipments.html', {'form': form, 'error': f"Error processing file: {e}"})
    else:
        form = ExcelUploadForm()

    # Fetch all shipment records from the database
    shipments = Shipment.objects.all()

    return render(request, 'shipments/shipments.html', {'form': form, 'shipments': shipments})
