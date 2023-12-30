from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from authapi.serializers import UserRegistationSerilizer, UserLoginSerilizer, UserChangePasswordSerializer, \
    SendVerificationCodeSerializer,  ResetPasswordSerializer
from authapi.models import User, VerificationCode
from django.contrib.auth import authenticate
from authapi.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from authapi.utils import Util, generate_verification_code_with_timestamp, generate_verification_code, \
    validate_verification_code


# creating token manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# Create your views here.
@api_view(['POST'])
@renderer_classes([UserRenderer])
def UserRegistration(request):
    if request.method == 'POST':
        serializer = UserRegistationSerilizer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"Registration successful": "success"},
                        status=status.HTTP_201_CREATED)


@api_view(['POST'])
@renderer_classes([UserRenderer])
def UserLogin(request):
    if request.method == 'POST':
        serializer = UserLoginSerilizer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            token = get_tokens_for_user(user)
            return Response({
                "Token": token, "Login": "succeess"},
                status=status.HTTP_200_OK)
        else:
            return Response({'errors': {'non_field_errors': ['Email or Password is incorrect']}},
                            status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@renderer_classes([UserRenderer])
@permission_classes([IsAuthenticated])
def ChangePassword(request):
    serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
    serializer.is_valid(raise_exception=True)
    return Response({'msg': 'Password Changed Successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@renderer_classes([UserRenderer])
def send_verification_code(request, *args, **kwargs):
    serializer = SendVerificationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({'msg': 'Verification code sent. Please check your email'}, status=status.HTTP_200_OK)


# @api_view(['POST'])
# @renderer_classes([UserRenderer])
# def verify_verification_code(request, *args, **kwargs):
#     serializer = VerifyVerificationCodeSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)

# Retrieve the user based on the email provided in the request data
# email = serializer.validated_data['email']
# try:
#     user = User.objects.get(email=email)
# except User.DoesNotExist:
#     raise serializers.ValidationError('User not found')
#
# return Response({'msg': 'Verification code is valid'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@renderer_classes([UserRenderer])
def reset_password(request, *args, **kwargs):
    serializer = ResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Reset password logic
    verification_code_obj = VerificationCode.objects.get(
        # user__email=serializer.validated_data['email'],
        code=serializer.validated_data['verification_code']
    )

    email = verification_code_obj.user
    user = User.objects.get(email=email)
    user.set_password(serializer.validated_data['password'])
    user.save()
    verification_code_obj.used = True
    verification_code_obj.save()

    return Response({'msg': 'Password reset successfully'}, status=status.HTTP_200_OK)