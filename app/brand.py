import logging
import os
import sys
from functools import wraps
from http import HTTPStatus
from typing import Callable
from uuid import uuid4

import requests
from flask import Blueprint, Response, abort, jsonify, request
from pydantic.error_wrappers import ValidationError
from pyisemail import is_email
from requests.exceptions import HTTPError

import models
from app.data_types import Coupon, DiscountDescription, FanData

blueprint = Blueprint('brands', __name__)
LOG = logging.getLogger(__name__)
LOG.addHandler(logging.StreamHandler(sys.stdout))
LOG.propagate = False
EMAIL_VERIFIER = os.getenv('EMAIL_VERIFIER_URL', 'http://localhost:5001')
COUPON_REALIZER = os.getenv('COUPON_REALIZER_URL', 'http://localhost:5002')


def id_from_brand(brand: str) -> int:
    """This would normally be part of the loaded brand configuration."""
    return 1234


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
    LOG.debug(f'Registering fan data for {brand}')

    try:
        fan_data = FanData(**request.json)
    except ValidationError:
        LOG.warning('Bad data in POST request.')
        abort(HTTPStatus.BAD_REQUEST)

    if not is_email(fan_data.email):
        LOG.warning('Bad email in POST request.')
        abort(HTTPStatus.UNPROCESSABLE_ENTITY)

    fan_application = models.FanApplication(**fan_data.dict())
    fan_application.token = uuid4().hex
    fan_application.brand_id = id_from_brand(brand)

    discount = models.Discount.match_to_application(fan_application, id_from_brand(brand))
    if discount is None:
        LOG.warning('No Discount matches POST request.')
        abort(HTTPStatus.UNPROCESSABLE_ENTITY)

    fan_application.discount_id = discount.id

    if discount.verify_email:
        verification_body = {
            'email': fan_application.email,
            'token': fan_application.token,
            'brand': fan_application.brand_id,
        }

        try:
            r = requests.post(EMAIL_VERIFIER + '/email', json=verification_body)
            r.raise_for_status()
        except HTTPError:
            LOG.warning('Failed to queue email verification.')
            abort(HTTPStatus.SERVICE_UNAVAILABLE)

        # We've handed off the token, let's save it.
        # Save before or after the POST is an interesting discussion.
        fan_application.save()
        return 'OK'

    # No verification, simply create a coupon code directly
    coupon = Coupon.from_data(fan_application, discount)
    try:
        r = requests.post(COUPON_REALIZER + '/coupon', json=coupon.dict())
        r.raise_for_status()
    except HTTPError:
        LOG.warning('Failed to queue realization of coupon code.')
        abort(HTTPStatus.SERVICE_UNAVAILABLE)

    return 'OK'
