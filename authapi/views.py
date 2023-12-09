from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from authapi.serializers import UserRegistationSerilizer, UserLoginSerilizer, UserChangePasswordSerializer, \
    SendPasswordResetEmailSerializer, PasswordResetSerializer
from django.contrib.auth import authenticate
from authapi.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken


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
        return Response({"Registration": "success"},
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
def SendPasswordResetEmail(request):
    serializer = SendPasswordResetEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({'msg': 'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@renderer_classes([UserRenderer])
def ResetPassword(request, uid, token):
    serializer = PasswordResetSerializer(data=request.data, context={'uid': uid, 'token': token})
    serializer.is_valid(raise_exception=True)
    return Response({'msg': 'Password Reset Successfully'}, status=status.HTTP_200_OK)
