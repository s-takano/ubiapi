from datetime import datetime
from optparse import Option
from pydantic import BaseModel, validator
from typing import Optional, List

"""
Contains all schemas alias domain models of the application.
For domain modelling, the library pydantic is used.
Pydantic allows to create versatile domain models and ensures data integrity and much more.
"""


class CalculationOption(BaseModel):
    tax_rounding_mode: str  # "down",
    price_rounding_mode: str  # "plain",
    tax_calculation_level: str  # "checkout"

    class Config:
        fields = {
            "tax_rounding_mode": {"description": "down"},
            "price_rounding_mode": {"description": "plain"},
            "tax_calculation_level": {"description": "checkout"}
        }

class CheckoutPayment(BaseModel):
    ...

class CheckoutItem(BaseModel):
    ...

class CheckoutTax(BaseModel):
    ...

class CheckoutBase(BaseModel):
    """
    Checkout base schema
    """
    guid: str  # "8928309238-d987aerkeh-9847tdfkzhg4"
    device_id: str  # "710b52d6-9d8f-11e5-9aac-af957c6aaf43"
    account_id: int  # 1
    paid_at: datetime  # "2011-12-24T16:20:20Z"
    closed_at : datetime #": "2022-06-19T16:20:20Z",
    deleted_at : Optional[str] #": null,
    created_at : datetime #"2022-06-19T20:56:38Z",
    updated_at : datetime # "2022-06-19T20:56:38Z",
    opened_at : Optional[str] #: null,
    sales_date: str  #: "2011-12-25"
    price: str  # "385.0",
    change: str  # "4000.0"
    cashier_id : int #: 167226,
    status: str  # "close"
    # cashier_id: Optional[int] # null
    customers_count: int  # 0
    payments: List[CheckoutPayment]  # "[ $Payments]
    taxes: List[CheckoutTax]  # "[ $CheckoutTaxes]
    items: List[CheckoutItem]  # " [ $CheckoutItems]
    # table_ids : List[int] #" [99, 8]
    customer_tag_ids: List[int]  # [10, 1003]
    # modifier": "0.0",
    calculation_option: CalculationOption

    class Config:
        fields = {
            "guid": {"description": "8928309238-d987aerkeh-9847tdfkzhg4"},
            "device_id": {"description": "710b52d6-9d8f-11e5-9aac-af957c6aaf43"},
            "account_id": {"description": 1},
            "paid_at": {"description": "2011-12-24T16:20:20Z"},
            "closed_at" : {"description": "2022-06-19T16:20:20Z"},
            "deleted_at" : {"description": "null"},
            "created_at" : {"description": "2022-06-19T20:56:38Z"},
            "updated_at" : {"description": "2022-06-19T20:56:38Z"},
            "opened_at" : {"description": "null"},
            "sales_date": {"description": "2011-12-25"},
            "price": {"description": "385.0"},
            "change": {"description": "4000.0"},
            "cashier_id" : {"description": "167226"},
            "status": {"description": "close"},
            "customers_count": {"description": 0},
            "payments": {"description": "[ $Payments]"},
            "taxes": {"description": "[ $CheckoutTaxes]"},
            "items": {"description": "[ $CheckoutItems]"},
            "customer_tag_ids": {"description": "[10, 1003]"},
            "calculation_option": {"description": ""}
        }


class CheckoutCreate(CheckoutBase):
    """
    Checkout create schema
    """
    ...


class CheckoutPartialUpdate(CheckoutBase):
    """
    Checkout update schema
    """
    ...


class Checkout(CheckoutBase):
    """
    Checkout schema, database representation
    """
    id: int

    class Config:
        fields = {
            "id": {"description": "Unique ID of the checkout"},
        }


class CustomerTag(BaseModel):
    id : int #": 123,
    name : str #": "Dating",
    position : Optional[int] #": null,
    icon : Optional[str] #": $base64Encoded,
    icon_mime : str #": "image/png"


class PaymentType(BaseModel):
    id : int #": 207227,
    name : str #": "現金",
    enabled : bool #": true,
    change : bool #": true,
    position : int #": 0,
    kind : str #": "cash",
    marketable : bool #": false,
    icon_url : Optional[str] #": null,
    annotations : List[dict] #": [],
    restricted_by_default : bool #": false,
    allowed_category_ids : List[int] #": [],
    denied_category_ids : List[int] #": [],
    capped : bool #": false


class Cashier(BaseModel):
    id : int #": 167226,
    name : str #": "レジ1",
    enabled : bool #": true,
    created_at : datetime #": "2022-06-09T12:40:17Z",
    updated_at : datetime #": "2022-06-11T09:33:11Z"


class PriceBook(BaseModel):
    id : int #": 123,
    account_id : int #": 9744,
    name : str #": "Take Out",
    tax_rate : str #": "8.0",
    receipt_symbol : str #": "※",
    receipt_text : str #": "※印は軽減税率対象商品",
    tax_type : str #": null,
    position : int #": 1,
    valid_since : str #": "2019/10/01",
    valid_until : str #": "2020/09/30"

class Account(BaseModel):
        id : int # 36872,
        login : str # "someone",
        email : str # "someone@something.jp",
        name : str # "ビューティーセラーByハリウッド",
        expire_at : datetime #": "2022-07-09T12:40:00Z",
        subscription : str #": "trial",
        currency : str #": "JPY",
        lang : str #": "ja",
        date_offset : int #": 6,
        timezone : str #": "Asia/Tokyo",
        receipt_title : str #": "レシート",
        receipt_footer : str #": "住所やメッセージをここに記載します。 ユビレジWebサイトにログインし「レジ管理 → レシート」から設定を行います。",
        receipt_logo : Optional[str] #": null,
        stamp_tax_threshold : str #": "50000",
        stamp_tax_text : str #": "収　　入\n\n\n印　　紙",
        menus : List[int] #": [            36585        ],
        customer_tags : List[CustomerTag] #": [],
        payment_types : List[PaymentType] #
        paid_inout_reasons : List[str] #": [],
        cashiers : List[Cashier]
        price_books : List[PriceBook]
        #"barcode_rules": [],
        parent_ids : List[int] #": [],
        child_ids : List[int] #": [],
        sibling_ids : List[int] #": [],
        created_at : datetime #": "2022-06-09T12:40:16Z",
        updated_at : datetime #": "2022-06-11T09:33:11Z",
        # "devices": [
        #     {
        #         "guid": "e10cca69-25bf-49ed-98f0-7541eb2395a0",
        #         "name": "名前なし"
        #     }
        # ],
        setting_disabled : bool #": false,
        menu_group_editable : bool #": true,
        # "enabled_integration_modules": [],
        # "integration_settings": {},
        calculation_option : dict
        options : dict
        # inventory_enabled : null,
        # "settings": {}
