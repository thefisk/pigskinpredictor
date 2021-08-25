from django.forms import ModelForm
from .models import Record

class RecordsForm(ModelForm):
   class Meta:
        model = Record
        fields = ('Title', 'Holders', 'Year', 'Week', 'Record', 'Priority')