import datetime
from enum import Enum, auto
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel

import models


def generate_code() -> str:
    """Concievably this would be configurable, perhaps generating safe adjective-noun strings or more easily remembered phrases"""
    return uuid4().hex


class StrEnum(str, Enum):
    """Ref: https://docs.python.org/3.9/library/enum.html#using-automatic-values"""
    def _generate_next_value_(name: str, start, count, last_values) -> str:  # NOQA - ignore bad name for clarity
        return name


class DiscountType(StrEnum):
    PERCENT = auto()  # A fixed percentage off purchase
    FIXED_CART = auto()  # A fixed "dollar amount" off purchase
    # ... and so on


class DiscountDescription(BaseModel):
    name: str
    fixed_code: Optional[str]
    date_expires: datetime.date
    discount_type: DiscountType
    discount_amount: int
    description: Optional[str]
    usage_limit: Optional[int]
    free_shipping: Optional[bool]
    verify_email: Optional[bool]


class FanData(BaseModel):
    name: str
    email: str
    facebook_handle: Optional[str]


class Coupon(BaseModel):
    fan_name: str
    email: str
    facebook_handle: Optional[str]
    discount_name: str
    coupon_code: str
    discount_type: DiscountType
    discount_amount: int
    description: Optional[str]
    usage_limit: Optional[int]
    free_shipping: Optional[bool]

    @classmethod
    def from_data(cls, fan: models.FanApplication, discount: models.Discount) -> 'Coupon':
        coupon_code = discount.fixed_code or generate_code()
        return Coupon(
            fan_name=fan.name,
            email=fan.email,
            facebook_handle=fan.facebook_handle,
            discount_name=discount.name,
            coupon_code=coupon_code,
            discount_type=discount.discount_type,
            discount_amount=discount.discount_amount,
            usage_limit=discount.usage_limit,
            free_shipping=discount.free_shipping
        )
