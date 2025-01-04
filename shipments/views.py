# views.py

import pandas as pd
from django.shortcuts import render
from .forms import ExcelUploadForm
from .models import Shipment
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
from datetime import datetime
from django.utils.timezone import now
from django.shortcuts import render, redirect
from django.contrib import messages



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



def clear_database(request):
    if request.method == "POST":
        # Delete all records in the Shipment model
        Shipment.objects.all().delete()
        messages.success(request, "All shipment records have been deleted.")
        return render(request, 'shipments/shipments.html')  # Temporarily render the same page




def packing_list(request):
    shipments = Shipment.objects.all()  # Fetch all shipments or filter as needed
    current_date = datetime.now()

    # Convert your queryset into a pandas DataFrame
    df = pd.DataFrame(list(shipments.values('box', 'cross_reference', 'pallet', 'description', 'qty')))

    df['qty'] = pd.to_numeric(df['qty'], errors='coerce')
    
    # Group by 'box' and 'cross_reference' and aggregate
    pivot_table = df.groupby(['box', 'cross_reference',  'description', 'pallet']).agg(
        count_cross_reference=('cross_reference', 'size'),  # Count occurrences of cross_reference in the box
        total_qty=('qty', 'sum')  # Calculate sum of qty for each group
    ).reset_index()

    pivot_table = pivot_table.to_dict(orient='records')

    total_qty = df['qty'].sum()

    print(pivot_table)


    return render(request, 'shipments/packing_list.html', {
        'shipments': shipments,
        'current_date': current_date,
        'pivot_table': pivot_table,  # Pass the pivot table to the template
        'total_qty': total_qty,  # Pass the total quantity to the template
    })



    # New function to generate packing list PDF for each pallet
def packing_list_pdf(request, pallet_id):
    # Fetch shipments for a specific pallet
    shipments = Shipment.objects.filter(pallet=pallet_id)

    current_date = datetime.now()

    # Convert the data to a DataFrame
    df = pd.DataFrame(list(shipments.values('serial_lot', 'item_number', 'cross_reference', 'description', 'qty', 'box', 'pallet', 'invoice')))

    # Group by 'cross_reference', 'description', and 'pallet' for the pivot table
    pivot_table = df.groupby(['box', 'cross_reference', 'description', 'pallet']).agg(
        total_qty=('qty', 'sum'),  # Sum the quantities for each group
        count_cross_reference=('cross_reference', 'size')  # Count occurrences of cross_reference
    ).reset_index()

    # Collect unique invoice numbers for the pallet
    unique_invoices = df['invoice'].dropna().unique()

    # Convert pivot table to dictionary for passing to template
    pivot_table = pivot_table.to_dict(orient='records')

    # Calculate total quantity and ensure it's numeric
    total_qty = pd.to_numeric(df['qty'], errors='coerce').sum()

    # Generate the HTML for the PDF
    html = render_to_string('shipments/packing_list_pdf.html', {
        'shipments': df.to_dict(orient='records'),
        'pivot_table': pivot_table,  # Pass the actual data as a list of dictionaries
        'pallet_id': pallet_id,
        'unique_invoices': unique_invoices,
        'total_qty': total_qty,  # Pass the total quantity to the template
        'current_date': current_date,  # Pass the current date to the template
    })

    # Generate the PDF
    pdf = HTML(string=html).write_pdf()

    # Return the PDF as an HTTP response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="packing_list_{pallet_id}.pdf"'
    return response
