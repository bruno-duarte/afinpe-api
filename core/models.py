import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class Person(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firstName = models.TextField(null=True, blank=True)
    lastName = models.TextField(null=True, blank=True)
    fullName = models.TextField()
    image = models.TextField(null=True, blank=True)
    status = models.IntegerField(default=1)

    def __str__(self):
        return self.fullName

class User(AbstractUser):
    # Replace default id with UUID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)  # maps 'login'
    # password provided by AbstractUser (hashed)
    created = models.TextField(null=True, blank=False)
    modified = models.TextField(null=True, blank=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="users")

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "person"]

class Color(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField(null=True, blank=True)
    hexadecimal = models.TextField(null=True, blank=True)
    rgba = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

class Icon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    set = models.TextField()

class Bank(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.TextField(null=True, blank=True)
    name = models.TextField()
    image = models.TextField(null=True, blank=True)

class Currency(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symbol = models.TextField(null=True, blank=True)
    code = models.TextField()
    number = models.TextField(null=True, blank=True)
    minorUnit = models.IntegerField(default=2)
    image = models.TextField(unique=True)
    type = models.IntegerField(default=1)
    countryCode = models.TextField(null=True, blank=True)

class BankAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    type = models.IntegerField()
    operation = models.TextField(null=True, blank=True)
    accountNumber = models.TextField(null=True, blank=True)
    accountDigit = models.TextField(null=True, blank=True)
    agencyNumber = models.TextField(null=True, blank=True)
    agencyDigit = models.TextField(null=True, blank=True)
    initialBalance = models.IntegerField()
    created = models.TextField()
    modified = models.TextField()
    bank = models.ForeignKey(Bank, null=True, blank=True, on_delete=models.SET_NULL)
    color = models.ForeignKey(Color, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bankJson = models.TextField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)

class BankAccountLimit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    translationKey = models.TextField()
    type = models.IntegerField()
    value = models.IntegerField()
    bankAccount = models.ForeignKey(BankAccount, on_delete=models.CASCADE)

class CreditCardFlag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    image = models.TextField(null=True, blank=True)

class CreditCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.TextField()
    modified = models.TextField()
    name = models.TextField()
    limitValue = models.IntegerField()
    closingDay = models.IntegerField()
    dueDate = models.IntegerField()
    bankAccount = models.ForeignKey(BankAccount, null=True, blank=True, on_delete=models.CASCADE)
    creditCardFlag = models.ForeignKey(CreditCardFlag, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(null=True, blank=True)

class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.TextField()
    modified = models.TextField()
    status = models.IntegerField()
    closingDate = models.TextField()
    dueDate = models.TextField()
    paymentDate = models.TextField(null=True, blank=True)
    paymentAmount = models.IntegerField(null=True, blank=True)
    creditCard = models.ForeignKey(CreditCard, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField()
    type = models.IntegerField()
    icon = models.ForeignKey(Icon, on_delete=models.PROTECT)
    color = models.ForeignKey(Color, on_delete=models.PROTECT)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

class Subcategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    icon = models.ForeignKey(Icon, on_delete=models.PROTECT)
    color = models.ForeignKey(Color, on_delete=models.PROTECT)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

class Planning(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    month = models.IntegerField()
    year = models.IntegerField()
    monthlyIncome = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)

class Budget(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plannedValue = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    subcategory = models.ForeignKey(Subcategory, null=True, blank=True, on_delete=models.SET_NULL)
    planning = models.ForeignKey(Planning, on_delete=models.CASCADE)

class Loan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.TextField()
    modified = models.TextField()
    description = models.TextField()
    principalAmount = models.IntegerField()
    totalAmount = models.IntegerField()
    dueDate = models.TextField()
    type = models.IntegerField()
    bankAccount = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    icon = models.ForeignKey(Icon, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.TextField()
    modified = models.TextField()
    date = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    originalValue = models.IntegerField(null=True, blank=True)
    value = models.IntegerField()
    observation = models.TextField(null=True, blank=True)
    ignore = models.IntegerField(null=True, blank=True)
    isTransfer = models.IntegerField()
    isCreditCardTransaction = models.IntegerField()
    paid = models.IntegerField(null=True, blank=True)
    fixed = models.IntegerField(null=True, blank=True)
    fixedDay = models.IntegerField(null=True, blank=True)
    type = models.IntegerField()
    paymentDate = models.TextField(null=True, blank=True)
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.CASCADE)
    bankAccount = models.ForeignKey(BankAccount, null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    groupingId = models.TextField(null=True, blank=True)
    invoiceNumber = models.IntegerField(null=True, blank=True)
    isReturn = models.IntegerField(null=True, blank=True)
    invoiceValue = models.IntegerField(null=True, blank=True)
    originalDate = models.TextField(null=True, blank=True)
    partialPaymentId = models.TextField(null=True, blank=True)
    canEdit = models.IntegerField(null=True, blank=True)
    subcategory = models.ForeignKey(Subcategory, null=True, blank=True, on_delete=models.SET_NULL)
    loan = models.ForeignKey(Loan, null=True, blank=True, on_delete=models.SET_NULL)

class Goal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.TextField()
    modified = models.TextField()
    completionDate = models.IntegerField()
    type = models.IntegerField()
    description = models.IntegerField()
    aimValue = models.IntegerField()
    image = models.TextField(null=True, blank=True)
    rememberDay = models.IntegerField(null=True, blank=True)
    bankAccount = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    color = models.ForeignKey(Color, null=True, blank=True, on_delete=models.CASCADE)
    icon = models.ForeignKey(Icon, null=True, blank=True, on_delete=models.CASCADE)
    initialValue = models.IntegerField(default=0)

class GoalTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)

class Alert(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField()
    created = models.TextField()
    readDateTime = models.TextField(null=True, blank=True)
    userActionScreen = models.TextField(null=True, blank=True)
    screenParams = models.TextField(null=True, blank=True)
    buttonTitle = models.TextField(null=True, blank=True)
    userActionModal = models.IntegerField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    translationKeyMessage = models.TextField(null=True, blank=True)
    translationKeyButton = models.TextField(null=True, blank=True)
    translationObj = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Alert({self.id})"
