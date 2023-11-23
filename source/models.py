from enum import IntEnum, Enum
from tortoise import Model
from tortoise.fields import BigIntField, ForeignKeyRelation, ForeignKeyField, ReverseRelation, TextField, OnDelete, \
    BinaryField, DateField, IntEnumField, CharField, CharEnumField, DecimalField


class SupportBankName(str, Enum):
    tinkoff = "Тинькофф"
    module = "Модуль"
    tochka = "Точка"
    ozon = "Ozon"


class SupportBank(Model):
    id = BigIntField(pk=True)
    name = CharEnumField(enum_type=SupportBankName, description='Название банка', null=False)
    logo_url = TextField(maxlength=320, null=True, default='')
    user_banks: ReverseRelation['UserBank']
    data_collects: ReverseRelation['DataCollect']

    class Meta:
        table = "support_banks"


class UserBank(Model):
    id = BigIntField(pk=True)
    user_id = CharField(max_length=100, null=False, index=True)
    support_bank: ForeignKeyRelation['SupportBank'] = ForeignKeyField('models.SupportBank', on_delete=OnDelete.CASCADE,
                                                                      related_name="user_banks", null=False)
    payment_accounts: ReverseRelation['PaymentAccount']
    name = CharField(max_length=50, null=False)
    token = BinaryField(null=False)

    class Meta:
        table = "user_banks"


class PaymentAccountStatus(IntEnum):
    active = 1
    close = 0


class PaymentAccount(Model):
    id = BigIntField(pk=True)
    legal_entity_id = CharField(max_length=100, null=False, index=True)
    user_bank: ForeignKeyRelation['UserBank'] = ForeignKeyField('models.UserBank', on_delete=OnDelete.CASCADE,
                                                                related_name="payment_accounts", null=False)
    data_collects: ReverseRelation['PaymentAccount']
    start_date = DateField(null=False)
    last_date = DateField(null=True)
    number = CharField(max_length=50, null=False)
    status = IntEnumField(enum_type=PaymentAccountStatus, description="Статус расчётного счета", default=1)

    class Meta:
        table = "payment_accounts"


class DataCollectType(str, Enum):
    income = "Доход"
    cost = "Расход"


class DataCollect(Model):
    id = BigIntField(pk=True)
    payment_account: ForeignKeyRelation['PaymentAccount'] = ForeignKeyField('models.PaymentAccount',
                                                                            on_delete=OnDelete.CASCADE,
                                                                            related_name="data_collects", null=False)
    support_bank: ForeignKeyRelation['SupportBank'] = ForeignKeyField('models.SupportBank',
                                                                      on_delete=OnDelete.RESTRICT,
                                                                      related_name="data_collects", null=False)
    trxn_date = DateField(null=False, index=True)
    executor_chat_id = CharField(max_length=50, default='Нет chat_id', null=True)
    executor_name = CharField(max_length=100, null=False)
    type = CharEnumField(enum_type=DataCollectType, description='Тип операции', null=False)
    amount = DecimalField(max_digits=19, decimal_places=2, null=False)
    contragent_inn = CharField(max_length=30, default='', null=True)

    class Meta:
        table = "data_collects"
