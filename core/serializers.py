from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import (
    Person, User, Color, Icon, Bank, Currency, BankAccount, BankAccountLimit,
    CreditCardFlag, CreditCard, Invoice, Category, Subcategory, Planning, Budget,
    Loan, Transaction, Goal, GoalTransaction, Alert
)
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    personId = serializers.UUIDField(source="person.id", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "personId", "created", "modified"]
        read_only_fields = ["id", "created", "modified", "personId"]

    def update(self, instance, validated_data):
        instance.modified = timezone.now().isoformat()
        return super().update(instance, validated_data)

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "person"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = "__all__"

class IconSerializer(serializers.ModelSerializer):
    class Meta:
        model = Icon
        fields = "__all__"

class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = "__all__"

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = "__all__"

class BankAccountSerializer(serializers.ModelSerializer):
    colorId = serializers.PrimaryKeyRelatedField(
        source="color", queryset=Color.objects.all(), write_only=True
    )
    userId = serializers.PrimaryKeyRelatedField(
        source="user", queryset=User.objects.all(), write_only=True
    )
    bankId = serializers.PrimaryKeyRelatedField(
        source="bank", queryset=Bank.objects.all(), write_only=True, allow_null=True, required=False
    )
    currencyId = serializers.PrimaryKeyRelatedField(
        source="currency", queryset=Currency.objects.all(), write_only=True
    )

    color = ColorSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    bank = BankSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)

    class Meta:
        model = BankAccount
        fields = [
            "id",
            "name",
            "type",
            "operation",
            "accountNumber",
            "accountDigit",
            "agencyNumber",
            "agencyDigit",
            "initialBalance",
            "created",
            "modified",
            "bankId",
            "colorId",
            "userId",
            "currencyId",
            "bank",
            "color",
            "user",
            "currency",
            "bankJson",
            "status",
        ]

    def create(self, validated_data):
        account = BankAccount.objects.create(**validated_data)
        return BankAccount.objects.select_related(
            "color", "user", "bank", "currency"
        ).get(pk=account.pk)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return BankAccount.objects.select_related(
            "color", "user", "bank", "currency"
        ).get(pk=instance.pk)

class BankAccountLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccountLimit
        fields = "__all__"

class CreditCardFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditCardFlag
        fields = "__all__"

class CreditCardSerializer(serializers.ModelSerializer):
    bankAccountId = serializers.PrimaryKeyRelatedField(
        source="bankAccount", queryset=BankAccount.objects.all(), write_only=True
    )
    creditCardFlagId = serializers.PrimaryKeyRelatedField(
        source="creditCardFlag", queryset=CreditCardFlag.objects.all(), write_only=True
    )
    userId = serializers.PrimaryKeyRelatedField(
        source="user", queryset=User.objects.all(), write_only=True
    )

    bankAccount = BankAccountSerializer(read_only=True)
    creditCardFlag = CreditCardFlagSerializer(read_only=True)

    class Meta:
        model = CreditCard
        fields = [
            "id",
            "created",
            "modified",
            "name",
            "limitValue",
            "closingDay",
            "dueDate",
            "status",
            "bankAccount",
            "bankAccountId",
            "creditCardFlagId",
            "creditCardFlag",
            "userId",
        ]

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = "__all__"

class SubcategorySerializer(serializers.ModelSerializer):
    categoryId = serializers.PrimaryKeyRelatedField(
        source="category", queryset=Category.objects.all(), write_only=True
    )
    iconId = serializers.PrimaryKeyRelatedField(
        source="icon", queryset=Icon.objects.all(), write_only=True
    )
    colorId = serializers.PrimaryKeyRelatedField(
        source="color", queryset=Color.objects.all(), write_only=True
    )
    userId = serializers.PrimaryKeyRelatedField(
        source="user", queryset=User.objects.all(), write_only=True
    )

    color = ColorSerializer(read_only=True)
    icon = IconSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Subcategory
        fields = [
            "id",
            "description",
            "categoryId",
            "iconId",
            "colorId",
            "userId",
            "color",
            "icon",
            "user",
        ]

    def to_representation(self, instance):
        """
        Customiza a representação do objeto para incluir 'categoryId'.
        """
        representation = super().to_representation(instance)
        representation['categoryId'] = instance.category.id
        
        return representation

class CategorySerializer(serializers.ModelSerializer):
    iconId = serializers.PrimaryKeyRelatedField(
        source="icon", queryset=Icon.objects.all(), write_only=True
    )
    colorId = serializers.PrimaryKeyRelatedField(
        source="color", queryset=Color.objects.all(), write_only=True
    )
    userId = serializers.PrimaryKeyRelatedField(
        source="user", queryset=User.objects.all(), write_only=True
    )

    color = ColorSerializer(read_only=True)
    icon = IconSerializer(read_only=True)
    subcategories = SubcategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "description",
            "type",
            "iconId",
            "colorId",
            "userId",
            "color",
            "icon",
            "subcategories",
        ]

    def create(self, validated_data):
        category = Category.objects.create(**validated_data)
        return Category.objects.select_related("color", "icon").prefetch_related("subcategories").get(pk=category.pk)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return Category.objects.select_related("color", "icon").prefetch_related("subcategories").get(pk=instance.pk)


class PlanningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planning
        fields = "__all__"

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = "__all__"

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = "__all__"

class TransactionSerializer(serializers.ModelSerializer):
    userId = serializers.PrimaryKeyRelatedField(
        source="user", queryset=User.objects.all(), write_only=True
    )

    invoiceId = serializers.PrimaryKeyRelatedField(
        source="invoice", queryset=Invoice.objects.all(), write_only=True,required=False, allow_null=True
    )

    bankAccountId = serializers.PrimaryKeyRelatedField(
        source="bankAccount", queryset=BankAccount.objects.all(), write_only=True
    )

    categoryId = serializers.PrimaryKeyRelatedField(
        source="category", queryset=Category.objects.all(), write_only=True
    )

    subcategoryId = serializers.PrimaryKeyRelatedField(
        source="subcategory", queryset=Subcategory.objects.all(), write_only=True,required=False, allow_null=True
    )

    loanId = serializers.PrimaryKeyRelatedField(
        source="loan", queryset=Loan.objects.all(), write_only=True, required=False, allow_null=True
    )

    bankAccount = BankAccountSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    subcategory = SubcategorySerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "created",
            "modified",
            "date",
            "description",
            "originalValue",
            "value",
            "observation",
            "ignore",
            "isTransfer",
            "isCreditCardTransaction",
            "paid",
            "fixed",
            "fixedDay",
            "type",
            "paymentDate",
            "groupingId",
            "invoiceNumber",
            "isReturn",
            "invoiceValue",
            "originalDate",
            "partialPaymentId",
            "canEdit",
            "bankAccountId",
            "invoiceId",
            "categoryId",
            "subcategoryId",
            "loanId",
            "userId",
            "category",
            "bankAccount",
            "subcategory",
        ]

class GoalSerializer(serializers.ModelSerializer):
    bankAccountId = serializers.PrimaryKeyRelatedField(
        source="bankAccount", queryset=BankAccount.objects.all(), write_only=True
    )
    iconId = serializers.PrimaryKeyRelatedField(
        source="icon", queryset=Icon.objects.all(), write_only=True
    )
    colorId = serializers.PrimaryKeyRelatedField(
        source="color", queryset=Color.objects.all(), write_only=True
    )
    userId = serializers.PrimaryKeyRelatedField(
        source="user", queryset=User.objects.all(), write_only=True
    )

    bankAccount = BankAccountSerializer(read_only=True)
    color = ColorSerializer(read_only=True)
    icon = IconSerializer(read_only=True)

    class Meta:
        model = Goal
        fields = [
            "id",
            "created",
            "modified",
            "completionDate",
            "type",
            "description",
            "aimValue",
            "image",
            "rememberDay",
            "initialValue",
            "bankAccountId",
            "iconId",
            "colorId",
            "userId",
            "bankAccount",
            "color",
            "icon",
        ]

    def create(self, validated_data):
        goal = Goal.objects.create(**validated_data)
        return Goal.objects.select_related("bankAccount", "color", "icon").get(pk=goal.pk)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return Goal.objects.select_related("bankAccount", "color", "icon").get(pk=instance.pk)

class GoalTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalTransaction
        fields = "__all__"

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = "__all__"

class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    firstName = serializers.CharField(required=False, allow_blank=True)
    lastName = serializers.CharField(required=False, allow_blank=True)
    image = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def create(self, validated_data):
        full_name = f"{validated_data.get('firstName', '')} {validated_data.get('lastName', '')}".strip()

        person = Person.objects.create(
            firstName=validated_data.get("firstName", ""),
            lastName=validated_data.get("lastName", ""),
            fullName=full_name,
            image=validated_data.get("image", ""),
        )

        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            password=make_password(validated_data["password"]),
            person=person,
            is_staff=False,
            is_superuser=False,
            created=timezone.now().isoformat(),
            modified=timezone.now().isoformat(),
        )
        return user

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()  # Revoga o refresh token
        except Exception:
            raise serializers.ValidationError("Token inválido ou já expirado")

class SocialLoginSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=["google", "apple"])
    id_token = serializers.CharField()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer para retornar access/refresh + dados do usuário
    """
    def validate(self, attrs):
        data = super().validate(attrs)  # retorna access/refresh

        # Adiciona os dados do usuário
        user = self.user
        data.update({
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "first_name": getattr(user, "first_name", ""),
            "last_name": getattr(user, "last_name", ""),
            "personId": str(user.person.id) if user.person else None,
        })
        return data
