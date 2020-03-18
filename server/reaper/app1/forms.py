from django import forms

class TaskForm(forms.Form):
    task_domain = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control'}), max_length=50)