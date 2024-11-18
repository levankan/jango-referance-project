from django import forms

class DropDownForm(forms.Form):
    OPTIONS = [
        ('D638', 'D638'),
        ('D640', 'D640'),
        ('D635', 'D635'),
        ('NoN', 'NoN'),
    ]
    choices = forms.ChoiceField(choices=OPTIONS, label="Choose an option")
    contact_email = forms.EmailField(label="Your Email")
    comment = forms.CharField(widget=forms.Textarea, label="Your Message")
