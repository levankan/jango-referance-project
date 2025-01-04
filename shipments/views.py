# views.py

import pandas as pd
from django.shortcuts import render
from .forms import ExcelUploadForm
from .models import Shipment, PalletDimension 
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

                # Check for duplicates in the file
                if df['serial_lot'].duplicated().any():
                    duplicates = df[df['serial_lot'].duplicated()]['serial_lot'].unique()
                    return render(request, 'shipments/shipments.html', {
                        'form': form,
                        'error': f"Duplicate serial numbers in the uploaded file: {', '.join(duplicates)}"
                    })

                # Check for duplicates in the database
                db_duplicates = []
                for serial in df['serial_lot']:
                    if Shipment.objects.filter(serial_lot=serial).exists():
                        db_duplicates.append(serial)

                if db_duplicates:
                    return render(request, 'shipments/shipments.html', {
                        'form': form,
                        'error': f"Duplicate serial numbers found in the database: {', '.join(db_duplicates)}"
                    })

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

                # After saving Shipments, fetch all shipments
                shipments_qs = Shipment.objects.all()

                # Find unique pallets from the uploaded DataFrame
                unique_pallets = df['pallet'].dropna().unique().tolist()

                return render(
                    request,
                    'shipments/shipments.html',
                    {
                        'form': form,
                        'shipments': shipments_qs,
                        'success': 'File uploaded and data saved successfully.',
                        'unique_pallets': unique_pallets,
                    }
                )
            except Exception as e:
                return render(request, 'shipments/shipments.html', {
                    'form': form,
                    'error': f"Error processing file: {e}"
                })
    else:
        form = ExcelUploadForm()

    # If GET or no valid form, just render normally
    shipments_qs = Shipment.objects.all()
    return render(request, 'shipments/shipments.html', {
        'form': form,
        'shipments': shipments_qs
    })




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
    from django.shortcuts import get_object_or_404
    
    shipments = Shipment.objects.filter(pallet=pallet_id)
    current_date = datetime.now()

    # Convert the data to a DataFrame
    df = pd.DataFrame(
        list(shipments.values('serial_lot', 'item_number', 'cross_reference', 
                              'description', 'qty', 'box', 'pallet', 'invoice'))
    )

    # Group by 'box', 'cross_reference', 'description', 'pallet' for the pivot table
    pivot_df = df.groupby(['box', 'cross_reference', 'description', 'pallet']).agg(
        total_qty=('qty', 'sum'),
        count_cross_reference=('cross_reference', 'size')
    ).reset_index()

    # Convert pivot table to dictionary
    pivot_table = pivot_df.to_dict(orient='records')

    #Merge dimension info for each row
    for row in pivot_table:
        pal_number = str(row['pallet'])  # Convert to string if needed
        try:
            p_dim = PalletDimension.objects.get(pallet_number=pal_number)
            row['dimension_string'] = f"{p_dim.length_cm} X {p_dim.width_cm} X {p_dim.height_cm} cm"
        except PalletDimension.DoesNotExist:
            row['dimension_string'] = "N/A"


    # Unique invoices
    unique_invoices = df['invoice'].dropna().unique()
    total_qty = pd.to_numeric(df['qty'], errors='coerce').sum()

    # Render the PDF
    html = render_to_string('shipments/packing_list_pdf.html', {
        'shipments': df.to_dict(orient='records'),
        'pivot_table': pivot_table,
        'pallet_id': pallet_id,
        'unique_invoices': unique_invoices,
        'total_qty': total_qty,
        'current_date': current_date,
    })

    pdf = HTML(string=html).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=\"packing_list_{pallet_id}.pdf\"'
    return response




    # views.py
def save_dimensions(request):
    if request.method == "POST":
        # We'll parse all keys in request.POST
        dimension_data = {}
        for key, value in request.POST.items():
            if key.startswith("length_"):
                # e.g., length_PalletA
                pallet = key.replace("length_", "")
                if pallet not in dimension_data:
                    dimension_data[pallet] = {}
                dimension_data[pallet]['length'] = value
            elif key.startswith("width_"):
                pallet = key.replace("width_", "")
                if pallet not in dimension_data:
                    dimension_data[pallet] = {}
                dimension_data[pallet]['width'] = value
            elif key.startswith("height_"):
                pallet = key.replace("height_", "")
                if pallet not in dimension_data:
                    dimension_data[pallet] = {}
                dimension_data[pallet]['height'] = value

        # dimension_data now might look like:
        # {
        #   "PalletA": {"length": "120", "width": "80", "height": "25"},
        #   "PalletB": {"length": "100", "width": "70", "height": "30"},
        # }

        # Store them in your model, e.g., PalletDimension or in Shipment if unique
        for pallet_id, dims in dimension_data.items():
            # Convert strings to integers
            length_val = int(dims['length']) if dims['length'] else 0
            width_val = int(dims['width']) if dims['width'] else 0
            height_val = int(dims['height']) if dims['height'] else 0

            # Example: if you have a separate PalletDimension model
            PalletDimension.objects.update_or_create(
                pallet_number=pallet_id,
                defaults={
                    'length_cm': length_val,
                    'width_cm': width_val,
                    'height_cm': height_val
                }
            )

        messages.success(request, "Dimensions saved!")
        return redirect('shipments')

    # If GET, just redirect back
    return redirect('shipments')
