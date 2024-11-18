from django.shortcuts import render
from .forms import DropDownForm
from .models import ChoiceRecord
import random

def home(request):
    # Initialize the form
    form = DropDownForm(request.POST or None)
    saved_record = None  # To store the record if saved

    if request.method == 'POST' and form.is_valid():
        # Get the selected option from the form
        selected_option = form.cleaned_data['choices']
        random_id = random.randint(1, 100000)

        # Save the selected option and random ID to the database
        saved_record = ChoiceRecord.objects.create(
            random_id=random_id,
            selected_option=selected_option
        )

    # Retrieve all records from the database
    data = ChoiceRecord.objects.all()

    # Pass data to the template
    context = {
        'id': random.randint(1, 100000),  # Generate a random ID
        'form': form,  # Form for dropdown options
        'saved_record': saved_record,  # Record saved after form submission
        'data': data,  # All records from the database
    }

    return render(request, 'home.html', context)
