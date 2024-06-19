from django import forms
from .models import OceanCurrentData
from .models import User
from django.contrib.auth.hashers import make_password
import datetime

class UploadFileForm(forms.Form):
    file = forms.FileField()

class SearchForm(forms.Form):
    station = forms.ChoiceField(label='站点', choices=[])
    date = forms.DateField(label='日期', widget=forms.SelectDateWidget(years=range(1900, 2030)))
    time = forms.ChoiceField(label='时间', choices=[(f"{hour:02d}:00", f"{hour:02d}:00") for hour in range(24)])

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['station'].choices = [(station, station) for station in OceanCurrentData.objects.values_list('station', flat=True).distinct()]

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['Username', 'Identity', 'Name', 'Gender', 'IDCard', 'PhoneNumber', 'Email']
        widgets = {
            'Identity': forms.Select(choices=[('tourist', '普通游客'), ('researcher', '科研人员'), ('manager', '管理人员')]),
            'Gender': forms.Select(choices=[('male', '男'), ('female', '女')]),
        }

class AnalysisForm(forms.Form):
    DIMENSION_CHOICES = [
        ('visibility', 'Visibility'),
        ('air_temperature', 'Air Temperature'),
        ('wind_direction', 'Wind Direction'),
        ('wind_speed', 'Wind Speed'),
        ('air_pressure', 'Air Pressure'),
        ('sea_temperature', 'Sea Temperature'),
        ('wind_wave_height', 'Wind Wave Height'),
        ('wind_wave_period', 'Wind Wave Period'),
    ]

    station = forms.ChoiceField(label='选择站点', choices=[])
    dimension = forms.ChoiceField(choices=DIMENSION_CHOICES, label='选择数据维度')
    date = forms.DateField(label='选择日期', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    month = forms.CharField(label='选择月份', required=False, widget=forms.DateInput(attrs={'type': 'month'}))

    def __init__(self, *args, **kwargs):
        super(AnalysisForm, self).__init__(*args, **kwargs)
        self.fields['station'].choices = [(station, station) for station in OceanCurrentData.objects.values_list('station', flat=True).distinct()]

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        month = cleaned_data.get("month")

        if date and month:
            raise forms.ValidationError("请仅选择日期或月份中的一个。")
        if not date and not month:
            raise forms.ValidationError("请至少选择日期或月份中的一个。")

        if month:
            try:
                cleaned_data['month'] = datetime.datetime.strptime(month, '%Y-%m').date()
            except ValueError:
                raise forms.ValidationError("请输入有效的月份格式。")
        
        return cleaned_data