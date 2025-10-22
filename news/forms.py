from django import forms
from .models import News
from django.utils.html import strip_tags


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ["title", "content", "is_important"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 8}),
            "is_important": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "is_important": "Отметить как важную новость"
        }

    def clean_content(self):
        content = self.cleaned_data["content"]
        return strip_tags(content)
