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
    def clean_content(self):
        # content = self.cleaned_data['content']
        if len(content) < 5:
            raise forms.ValidationError('帳號或密碼錯誤')
        return content

class RegisterForm(forms.Form):
    username = forms.CharField(
        label="帳號",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="確認密碼",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        label="姓氏",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label="名字",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email=forms.EmailField(
        label="電子郵件",
        widget=forms.TextInput(attrs={"class":"form-control"})
    )