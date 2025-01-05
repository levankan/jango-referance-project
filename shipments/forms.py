from django import forms

class ExcelUploadForm(forms.Form):
    file = forms.FileField(
        label="Choose File",
        widget=forms.FileInput(attrs={'accept': '.xls,.xlsx'})
    )

