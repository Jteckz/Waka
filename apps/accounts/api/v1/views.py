from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.api.v1.serializers import RegisterSerializer, UserSerializer
from apps.accounts.services import register_user
from common.exceptions import ValidationError


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = register_user(
                phone=serializer.validated_data["phone"],
                password=serializer.validated_data["password"],
                role=serializer.validated_data["role"],
            )
        except ValidationError as e:
            return Response(e.to_envelope(), status=status.HTTP_400_BAD_REQUEST)
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    pass


class RefreshView(TokenRefreshView):
    pass


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def health(request):
    return Response({"status": "ok"})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
