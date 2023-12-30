from rest_framework import serializers
from authapi.models import User
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from authapi.utils import Util, generate_verification_code_with_timestamp, generate_verification_code, \
    validate_verification_code
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']


class UserRegistationSerilizer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'password2', 'tc', ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    # validating password and confrim password
    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')

        if password != password2:
            raise serializers.ValidationError("Password and Confrim Pasword doesn't match")
        return data

    def create(self, validate_data):
        return User.objects.create_user(**validate_data)


class UserLoginSerilizer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ['email', 'password']


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

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


# serializers.py
class SendVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, data):
        email = data.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            verification_code, timestamp = generate_verification_code_with_timestamp(user)
            print(user)
            print(verification_code)

            # Send email with the verification code
            body = f'Your verification code is: {verification_code} It will expire after 4 minutes.'
            data = {
                'subject': 'Verify Your Email',
                'body': body,
                'to_email': user.email
            }
            Util.send_email(data)
            return data
        else:
            raise serializers.ValidationError('You are not a Registered User')


class ResetPasswordSerializer(serializers.Serializer):
    verification_code = serializers.CharField(max_length=6)
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['verification_code', 'password', 'password2']  # Remove 'email'

    def validate(self, data):
        verification_code = data.get('verification_code')
        # print(verification_code)
        password = data.get('password')
        # print(password)
        password2 = data.get('password2')
        # print(password2)

        # Validate the verification code
        is_valid_code = validate_verification_code(verification_code)
        if not is_valid_code:
            raise serializers.ValidationError('Invalid verification code or expired')

        # Validate password
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password don't match")

        return data

