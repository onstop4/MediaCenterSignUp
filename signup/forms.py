from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from signup.models import StudentInfo


class StudentInfoForm(forms.ModelForm):
    class Meta:
        model = StudentInfo
        fields = ["id"]

    def clean_id(self):
        _id = self.cleaned_data.get("id", None)
        if _id and _id.isdigit():
            return _id
        raise ValidationError(_("ID can only contain digits."))
