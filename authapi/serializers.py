from rest_framework import serializers
from authapi.models import User
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from authapi.utils import Util



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']

class UserRegistationSerilizer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'password2','tc',]
        extra_kwargs={
            'password':{'write_only': True}
        }
    
    #validating password and confrim password
    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')

        if password !=password2:
            raise serializers.ValidationError("Password and Confrim Pasword doesn't match")
        return data

    def create(self, validate_data):
        return User.objects.create_user(**validate_data)

class UserLoginSerilizer(serializers.ModelSerializer):
    email= serializers.EmailField(max_length=255)
    class Meta:
        model = User
        fields = ['email','password']


class UserChangePasswordSerializer(serializers.Serializer):
  old_password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  class Meta:
    fields = ['old_password', 'password', 'password2']

  def validate(self, data):
    old_password = data.get('old_password')
    password = data.get('password')
    password2 = data.get('password2')
    user = self.context.get('user')
    if not user.check_password(old_password):
        raise serializers.ValidationError("Old password is incorrect")

    if password != password2:
      raise serializers.ValidationError("Password and Confirm Password doesn't match")
    user.set_password(password)
    user.save()
    return data
      
class SendPasswordResetEmailSerializer(serializers.Serializer):
    email= serializers.EmailField(max_length=255)
    class Meta:
        fields= ['email']

    def validate(self, data):
        email = data.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = 'http://localhost:3000/api/user/resetpassword/'+uid+'/'+token
            print('Password Reset Link', link)
            #Send Emial

            body = 'Click Following Link to Reset Your Password '+link
            data = {
            'subject':'Reset Your Password',
            'body':body,
            'to_email':user.email
        }
            Util.send_email(data)
            return data

        else:
            raise serializers.ValidationError('You are not a Registered User')

class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)

    class Meta:
         fields =['password', 'password2']
    def validate(self, data):
        try:
            password = data.get('password')
            password2 = data.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')

            if password != password2:
                raise serializers.ValidationError("Password and Confirm Password doesn't match")

            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('Token is not Valid or Expired')

            user.set_password(password)
            user.save()
            return data

        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError('Token is not Valid or Expired')


