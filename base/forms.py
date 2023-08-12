from django.forms import ModelForm
from .models import Room

class RoomForm(ModelForm):
    class Meta:
        # we initialize model and field for which form should be rendered 
        model=Room
        fields="__all__"
        exclude=["host","participants"]
        
        
