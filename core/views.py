from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import (
    RegistrationSerializer, LogoutSerializer, SocialLoginSerializer, 
    MyTokenObtainPairSerializer
)
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

import requests

from .models import (
    Person, Color, Icon, Bank, Currency, BankAccount, BankAccountLimit,
    CreditCardFlag, CreditCard, Invoice, Category, Subcategory, Planning, Budget,
    Loan, Transaction, Goal, GoalTransaction, Alert
)
from .serializers import (
    PersonSerializer, UserSerializer, UserCreateSerializer, ColorSerializer, IconSerializer,
    BankSerializer, CurrencySerializer, BankAccountSerializer, BankAccountLimitSerializer,
    CreditCardFlagSerializer, CreditCardSerializer, InvoiceSerializer, CategorySerializer,
    SubcategorySerializer, PlanningSerializer, BudgetSerializer, LoanSerializer,
    TransactionSerializer, GoalSerializer, GoalTransactionSerializer, AlertSerializer,
    RegistrationSerializer
)
from .base import OptionalPaginationViewSet, BaseModelViewSet

User = get_user_model()

class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    http_method_names = ['get', 'put', 'patch', 'delete']

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @extend_schema(
    request=RegistrationSerializer,
    responses=OpenApiResponse(
        response=UserSerializer,
        description="Usuário criado com tokens JWT",
        examples=[
            OpenApiExample(
                'Exemplo de registro com tokens',
                value={
                    "id": "uuid-user",
                    "username": "joao123",
                    "email": "joao@email.com",
                    "personId": "uuid-person",
                    "created": "2025-08-24T10:15:00Z",
                    "modified": "2025-08-24T10:15:00Z",
                    "access": "jwt-access-token",
                    "refresh": "jwt-refresh-token"
                }
            )
        ]
    )
)
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def register(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)
            token_data = {"refresh": str(refresh), "access": str(refresh.access_token)}

            response_data = UserSerializer(user).data
            response_data.update(token_data)
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Logout realizado com sucesso"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ColorViewSet(OptionalPaginationViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer

class IconViewSet(OptionalPaginationViewSet):
    queryset = Icon.objects.all()
    serializer_class = IconSerializer

class BankViewSet(BaseModelViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer

class CurrencyViewSet(BaseModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

class BankAccountViewSet(BaseModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer

class BankAccountLimitViewSet(BaseModelViewSet):
    queryset = BankAccountLimit.objects.all()
    serializer_class = BankAccountLimitSerializer

class CreditCardFlagViewSet(BaseModelViewSet):
    queryset = CreditCardFlag.objects.all()
    serializer_class = CreditCardFlagSerializer

class CreditCardViewSet(BaseModelViewSet):
    queryset = CreditCard.objects.all()
    serializer_class = CreditCardSerializer

class InvoiceViewSet(BaseModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

class CategoryViewSet(OptionalPaginationViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class SubcategoryViewSet(OptionalPaginationViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

class PlanningViewSet(BaseModelViewSet):
    queryset = Planning.objects.all()
    serializer_class = PlanningSerializer

class BudgetViewSet(BaseModelViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer

class LoanViewSet(BaseModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

class TransactionViewSet(BaseModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class GoalViewSet(BaseModelViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer

class GoalTransactionViewSet(BaseModelViewSet):
    queryset = GoalTransaction.objects.all()
    serializer_class = GoalTransactionSerializer

class AlertViewSet(BaseModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer

class SocialLoginViewSet(viewsets.ViewSet):
    """
    ViewSet para login social com Google e Apple
    """

    def create(self, request):
        serializer = SocialLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = serializer.validated_data["provider"]
        token = serializer.validated_data["token"]

        if provider == "google":
            user_info = self._validate_google_token(token)
        elif provider == "apple":
            user_info = self._validate_apple_token(token)
        else:
            return Response(
                {"error": "Provedor inválido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user_info:
            return Response(
                {"error": "Token inválido"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            user = User.objects.get(email=user_info["email"])
        except User.DoesNotExist:
            return Response(
                {"error": "Usuário não encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # aqui você pode gerar o JWT ou usar sua forma de autenticação
        return Response(
            {
                "message": "Login realizado com sucesso",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.first_name,
                },
            }
        )

    def _validate_google_token(self, token):
        response = requests.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": token},
        )
        if response.status_code == 200:
            data = response.json()
            return {"email": data["email"], "name": data.get("name")}
        return None

    def _validate_apple_token(self, token):
        # Aqui pode usar pyjwt para verificar o JWT da Apple
        # ou consultar o endpoint da Apple
        # Exemplo simplificado:
        try:
            import jwt

            # você precisará buscar a chave pública da Apple:
            # https://appleid.apple.com/auth/keys
            decoded = jwt.decode(token, options={"verify_signature": False})
            return {"email": decoded.get("email")}
        except Exception:
            return None
        
class LoginViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @extend_schema(
        request=MyTokenObtainPairSerializer,  # serializer que define username/password
        responses=MyTokenObtainPairSerializer,  # mostra o que será retornado
        description="Login do usuário retornando JWT e dados do usuário"
    )
    def create(self, request):
        serializer = MyTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)