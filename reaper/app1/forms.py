from django import forms

class TaskForm(forms.Form):
    task_domain = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control'}), max_length=50)

class RecordForm(forms.Form):
    querytype = forms.ChoiceField(
        label="",
        initial=1,
        choices=((1, '网站域名'), (2, '主办单位'))
    )
    record = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control'}), max_length=50)
    # querytype = forms.CharField(label='',max_length=50,choices=(('1','网站域名'),('2','主办单位')),default='1')
    
    
