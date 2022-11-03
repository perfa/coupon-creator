import datetime
import logging
import sys
from enum import Enum, auto
from functools import wraps
from http import HTTPStatus
from typing import Callable, Optional

from flask import Blueprint, Response, abort, jsonify, request
from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError

import models

blueprint = Blueprint('brands', __name__)
LOG = logging.getLogger(__name__)
LOG.addHandler(logging.StreamHandler(sys.stdout))
LOG.propagate = False


def id_from_brand(brand: str) -> int:
    """This would normally be part of the loaded brand configuration."""
    return 1234


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


def require_auth_header(func: Callable) -> Callable:
    """A decorator to check for an Authorization token.
    Preferably this would be handled by a framework."""
    @wraps(func)
    def header_check(*args, **kwargs) -> Response:
        if 'X-API-Token' not in request.headers:
            LOG.warning(f'Unauthorized call to {request.base_url}')
            abort(HTTPStatus.UNAUTHORIZED)

        token = request.headers['X-API-Token']
        brand = kwargs.pop('brand')
        # This print is for seeing that it's working in this case, and not "part of
        # the system" as it would qbe in production
        print(f'Call authorized for brand  {brand} with token {token}')
        # TODO(perfa) - Validate token and pull up brand confiugration object
        kwargs['brand'] = brand  # Normally not just the name, see TODO

        return func(*args, **kwargs)
    return header_check


@blueprint.get('/')
def list_discounts() -> Response:
    session = models.db_root.session
    discounts = session.query(models.Discount).all()
    return jsonify([row.as_dict() for row in discounts])


@blueprint.post('/<brand>/discounts')
@require_auth_header
def create_discount(brand: str) -> Response:
    LOG.debug(f'Creating new discount for {brand}')

    try:
        discount = DiscountDescription(**request.json)
    except ValidationError:
        LOG.warning('Bad data in POST request.')
        abort(HTTPStatus.BAD_REQUEST)

    discount_row = models.Discount(**discount.dict())
    discount_row.brand_id = id_from_brand(brand)
    discount_row.save()

    return discount.name


@blueprint.put('/<brand>/discounts/<int:discount_id>')
@require_auth_header
def update_discount(brand: str, discount_id: int) -> Response:
    LOG.debug(f'Updating discount {discount_id} for {brand}')
    abort(HTTPStatus.NOT_IMPLEMENTED)


@blueprint.delete('/<brand>/discounts/<int:discount_id>')
@require_auth_header
def delete_discount(brand: str, discount_id: int) -> Response:
    LOG.debug(f'Deleting discount {discount_id} for {brand}')
    abort(HTTPStatus.NOT_IMPLEMENTED)


@blueprint.post('/<brand>/fans')
@require_auth_header
def new_fan(brand: str) -> Response:
    abort(HTTPStatus.NOT_IMPLEMENTED)
