from django import forms

class ExcelUploadForm(forms.Form):
    file = forms.FileField(
        label="Upload Excel File",
        widget=forms.FileInput(attrs={'accept': '.xls,.xlsx'})
    )
