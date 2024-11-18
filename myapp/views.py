from django.shortcuts import render
from .forms import DropDownForm
from .models import ChoiceRecord, ContactInfo
import random

def home(request):
    # Initialize the form
    form = DropDownForm(request.POST or None)
    saved_record = None  # To store the record if saved

    if request.method == 'POST' and form.is_valid():
        # Get the selected option from the form
        selected_option = form.cleaned_data['choices']
        random_id = random.randint(1, 100000)
        contact_email = form.cleaned_data.get('contact_email')  # Assuming you have a field in the form for email
        contact_message = form.cleaned_data.get('comment')  # Assuming you have a field for the message
        # Save the selected option and random ID to the database
        
        saved_record = ChoiceRecord.objects.create(
            random_id=random_id,
            selected_option=selected_option
        )

        ContactInfo.objects.create(
            email_area=contact_email,
            text_area=contact_message
        )

    # Retrieve all records from the database
    data = ChoiceRecord.objects.all()
    contct_info = ContactInfo.objects.all()

    # Pass data to the template
    context = {
        'id': random.randint(1, 100000),  # Generate a random ID
        'form': form,  # Form for dropdown options
        'saved_record': saved_record,  # Record saved after form submission
        'data': data,  # All records from the database
        'contct_info': contct_info
    }

    return render(request, 'home.html', context)
