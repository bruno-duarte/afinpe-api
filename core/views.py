from django.db.models import Sum, Q
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
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, OpenApiParameter, OpenApiTypes

import requests

from .models import (
    Person, Color, Icon, Bank, Currency, BankAccount, BankAccountLimit,
    CreditCardFlag, CreditCard, Invoice, Category, Subcategory, Planning, Budget,
    Loan, Transaction, Goal, GoalTransaction, Alert
)
from .serializers import (
    PersonSerializer, UserSerializer, ColorSerializer, IconSerializer,
    BankSerializer, CurrencySerializer, BankAccountSerializer, BankAccountLimitSerializer,
    CreditCardFlagSerializer, CreditCardSerializer, InvoiceSerializer, CategorySerializer,
    SubcategorySerializer, PlanningSerializer, BudgetSerializer, LoanSerializer,
    TransactionSerializer, GoalSerializer, GoalTransactionSerializer, AlertSerializer,
    RegistrationSerializer, PlanningSummaryResponseSerializer, PlanningCategoryItemSerializer
)
from .base import OptionalPaginationViewSet, BaseModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
import calendar

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

class BankViewSet(OptionalPaginationViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer

class CurrencyViewSet(OptionalPaginationViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

class BankAccountViewSet(OptionalPaginationViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer

class BankAccountLimitViewSet(BaseModelViewSet):
    queryset = BankAccountLimit.objects.all()
    serializer_class = BankAccountLimitSerializer

class CreditCardFlagViewSet(OptionalPaginationViewSet):
    queryset = CreditCardFlag.objects.all()
    serializer_class = CreditCardFlagSerializer

class CreditCardViewSet(OptionalPaginationViewSet):
    queryset = CreditCard.objects.all()
    serializer_class = CreditCardSerializer

class InvoiceViewSet(OptionalPaginationViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

class CategoryViewSet(OptionalPaginationViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class SubcategoryViewSet(OptionalPaginationViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

class PlanningViewSet(OptionalPaginationViewSet):
    queryset = Planning.objects.all()
    serializer_class = PlanningSerializer

class BudgetViewSet(OptionalPaginationViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer

class PlanningSummaryView(APIView):
    """
    Retorna o resumo do planejamento do mês com filtro opcional de moeda.
    Exemplo: /api/planning/summary/?user={user_id}&month=10&year=2024&currency=uuid
    """

    @extend_schema(
        description="Retorna o resumo do planejamento mensal, com filtro opcional por moeda.",
        parameters=[
            OpenApiParameter(name='user', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="ID do usuário", required=True),
            OpenApiParameter(name='month', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description="Mês (1–12)", required=True),
            OpenApiParameter(name='year', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description="Ano", required=True),
            OpenApiParameter(name='currency', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="UUID da moeda (opcional)", required=False),
        ],
        responses={
            200: PlanningSummaryResponseSerializer,
            400: OpenApiResponse(description="Parâmetros obrigatórios ausentes"),
            404: OpenApiResponse(description="Planejamento não encontrado")
        }
    )
    def get(self, request):
        user_id = request.query_params.get("user")
        month = request.query_params.get("month")
        year = request.query_params.get("year")
        currency_id = request.query_params.get("currency", None)

        if not all([user_id, month, year]):
            return Response({"detail": "Parâmetros obrigatórios: user, month, year"}, status=status.HTTP_400_BAD_REQUEST)

        planning = (
            Planning.objects
            .select_related("currency")
            .filter(user_id=user_id, month=month, year=year)
            .first()
        )

        if not planning:
            return Response({"detail": "Planejamento não encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Tipos de transação
        INCOME_TYPES = [2]       # receita
        EXPENSE_TYPES = [3, 5]   # despesa, despesa de cartão

        base_filter = {
            "user_id": user_id,
            "date__startswith": f"{year}-{int(month):02d}",
        }
        if currency_id:
            base_filter["bankAccount__currency_id"] = currency_id

        planned_total = planning.monthlyIncome or 0

        executed_total = (
            Transaction.objects
            .filter(**base_filter, type__in=EXPENSE_TYPES, paid=1)
            .aggregate(total=Sum("value"))["total"] or 0
        )

        pending_total = (
            Transaction.objects
            .filter(**base_filter, type__in=EXPENSE_TYPES, paid=0)
            .aggregate(total=Sum("value"))["total"] or 0
        )

        monthly_income = (
            Transaction.objects
            .filter(**base_filter, type__in=INCOME_TYPES)
            .aggregate(total=Sum("value"))["total"] or 0
        )

        currency_data = CurrencySerializer(planning.currency).data if planning.currency else None

        remaining = planned_total - executed_total
        days_in_month = calendar.monthrange(int(year), int(month))[1]
        available_per_day = remaining // days_in_month if days_in_month > 0 else 0

        response_data = {
            "id": str(planning.id),
            "planned": int(planned_total),
            "executed": int(executed_total),
            "pending": int(pending_total),
            "remaining": int(remaining),
            "monthlyIncome": int(monthly_income),
            "availablePerDay": int(available_per_day),
            "currency": currency_data,
        }

        return Response(response_data)

class PlanningCategoriesView(APIView):
    """
    Retorna o detalhamento do planejamento por categoria com filtro opcional de moeda.
    Exemplo: /api/planning/categories/?user={user_id}&month=10&year=2024&currency=uuid
    """

    @extend_schema(
        description="Retorna o detalhamento do planejamento por categoria, com filtro opcional por moeda.",
        parameters=[
            OpenApiParameter(name='user', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="ID do usuário", required=True),
            OpenApiParameter(name='month', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description="Mês (1–12)", required=True),
            OpenApiParameter(name='year', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description="Ano", required=True),
            OpenApiParameter(name='currency', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="UUID da moeda (opcional)", required=False),
        ],
        responses={
            200: PlanningCategoryItemSerializer(many=True),
            400: OpenApiResponse(description="Parâmetros obrigatórios ausentes"),
            404: OpenApiResponse(description="Planejamento não encontrado")
        }
    )
    def get(self, request):
        user_id = request.query_params.get("user")
        month = request.query_params.get("month")
        year = request.query_params.get("year")
        currency_id = request.query_params.get("currency")

        if not all([user_id, month, year]):
            return Response({"detail": "Parâmetros obrigatórios: user, month, year"}, status=400)

        planning = (
            Planning.objects
            .select_related("currency")
            .filter(user_id=user_id, month=month, year=year)
            .first()
        )
        if not planning:
            return Response({"detail": "Planejamento não encontrado"}, status=404)

        # Filtro base dos budgets
        budget_filter = {"planning_id": planning.id}
        if currency_id:
            budget_filter["planning__currency_id"] = currency_id

        budgets = (
            Budget.objects
            .filter(**budget_filter)
            .select_related("category", "category__icon")
        )

        # Tipos de transação de despesa
        expense_types = [3, 5]  # expense, creditCardExpense

        data = []
        for b in budgets:
            # Filtro base de transações da categoria
            transaction_filter = {
                "user_id": user_id,
                "category_id": b.category_id,
                "date__startswith": f"{year}-{int(month):02d}",
                "type__in": expense_types,
            }
            if currency_id:
                transaction_filter["bankAccount__currency_id"] = currency_id

            # Somatórios separados
            executed = (
                Transaction.objects.filter(**transaction_filter, paid=1)
                .aggregate(total=Sum("value"))["total"] or 0
            )
            pending = (
                Transaction.objects.filter(**transaction_filter, paid=0)
                .aggregate(total=Sum("value"))["total"] or 0
            )
            total_spent = executed + pending

            # Objeto da moeda do planejamento
            planning_currency = None
            if planning.currency:
                planning_currency = {
                    "id": str(planning.currency.id),
                    "code": planning.currency.code,
                    "symbol": planning.currency.symbol,
                    "minorUnit": planning.currency.minorUnit,
                }

            data.append({
                "id": str(b.id),
                "planningId": str(planning.id),
                "planningCurrency": planning_currency,
                "category": CategorySerializer(b.category).data,
                "planned": int(b.plannedValue),
                "executed": int(executed),
                "pending": int(pending),
                "totalSpent": int(total_spent),
            })

        return Response(data)

class LoanViewSet(BaseModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

class TransactionViewSet(OptionalPaginationViewSet):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        queryset = Transaction.objects.all()

        user_id = self.request.query_params.get("user")
        search = self.request.query_params.get("search")
        month = self.request.query_params.get("date__month")
        year = self.request.query_params.get("date__year")
        ordering = self.request.query_params.get("ordering", "-date")

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        if search:
            queryset = queryset.filter(
                Q(description__icontains=search)
                | Q(observation__icontains=search)
                | Q(category__description__icontains=search)
                | Q(subcategory__description__icontains=search)
            )

        if month and year:
            prefix = f"{year}-{int(month):02d}"
            queryset = queryset.filter(date__startswith=prefix)

        if ordering:
            queryset = queryset.order_by(ordering)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        total_income = queryset.filter(type__in=[4]).aggregate(total=Sum("value"))["total"] or 0
        total_expense = queryset.filter(type__in=[3, 5]).aggregate(total=Sum("value"))["total"] or 0
        total_balance = total_income - total_expense

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)

            paginated_response.data["summary"] = {
                "totalIncome": total_income,
                "totalExpense": total_expense,
                "balance": total_balance
            }
            return paginated_response

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "results": serializer.data,
            "summary": {
                "totalIncome": total_income,
                "totalExpense": total_expense,
                "balance": total_balance
            }
        })

class GoalViewSet(OptionalPaginationViewSet):
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