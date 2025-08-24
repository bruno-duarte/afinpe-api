from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.contrib.auth import get_user_model

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
    TransactionSerializer, GoalSerializer, GoalTransactionSerializer, AlertSerializer
)
from .permissions import IsAdmin

User = get_user_model()

class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = "__all__"
    ordering_fields = "__all__"

class PersonViewSet(BaseModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer

class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def signup(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_staff=False, is_superuser=False)
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], permission_classes=[IsAdmin])
    def admin_create_user(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ColorViewSet(BaseModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer

class IconViewSet(BaseModelViewSet):
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

class CategoryViewSet(BaseModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class SubcategoryViewSet(BaseModelViewSet):
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
