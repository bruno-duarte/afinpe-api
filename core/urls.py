from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenVerifyView
)
from .views import (
    PersonViewSet, UserViewSet, ColorViewSet, IconViewSet, BankViewSet, CurrencyViewSet,
    BankAccountViewSet, BankAccountLimitViewSet, CreditCardFlagViewSet, CreditCardViewSet,
    InvoiceViewSet, CategoryViewSet, SubcategoryViewSet, PlanningViewSet, BudgetViewSet,
    LoanViewSet, TransactionViewSet, GoalViewSet, GoalTransactionViewSet, AlertViewSet,
    SocialLoginViewSet
)

router = DefaultRouter()
router.register(r"people", PersonViewSet, basename="person")
router.register(r"users", UserViewSet, basename="user")
router.register(r"colors", ColorViewSet, basename="color")
router.register(r"icons", IconViewSet, basename="icon")
router.register(r"banks", BankViewSet, basename="bank")
router.register(r"currencies", CurrencyViewSet, basename="currency")
router.register(r"bank-accounts", BankAccountViewSet, basename="bankaccount")
router.register(r"bank-account-limits", BankAccountLimitViewSet, basename="bankaccountlimit")
router.register(r"credit-card-flags", CreditCardFlagViewSet, basename="creditcardflag")
router.register(r"credit-cards", CreditCardViewSet, basename="creditcard")
router.register(r"invoices", InvoiceViewSet, basename="invoice")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"subcategories", SubcategoryViewSet, basename="subcategory")
router.register(r"plannings", PlanningViewSet, basename="planning")
router.register(r"budgets", BudgetViewSet, basename="budget")
router.register(r"loans", LoanViewSet, basename="loan")
router.register(r"transactions", TransactionViewSet, basename="transaction")
router.register(r"goals", GoalViewSet, basename="goal")
router.register(r"goal-transactions", GoalTransactionViewSet, basename="goaltransaction")
router.register(r"alerts", AlertViewSet, basename="alert")
router.register("auth/social", SocialLoginViewSet, basename="social-auth")

urlpatterns = [
    # Auth endpoints (JWT)
    path("auth/jwt/create/", TokenObtainPairView.as_view(), name="jwt-create"),
    path("auth/jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("auth/jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),
    # Public signup and admin create
    path("", include(router.urls)),
]
