from django import forms

class CommentForm(forms.Form):
    visitor=forms.CharField(max_length=20)
    email=forms.EmailField(max_length=20,required=False,label='E-mail')
    content=forms.CharField(max_length=200,widget=forms.Textarea()) #widget 代表透過網頁哪個元件取得DATA
    def clean_content(self):
        content=self.cleaned_data['content']
        if len(content)<5:
            raise forms.ValidationError('字數不足')
        return content


class LoginForm(forms.Form):
    username = forms.CharField(
        label="帳號",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )