import logging
import os
import sys
from http import HTTPStatus

import requests
from flask import Blueprint, Response, abort
from requests.exceptions import HTTPError

import models
from app.data_types import Coupon

blueprint = Blueprint('fans', __name__)
LOG = logging.getLogger(__name__)
LOG.addHandler(logging.StreamHandler(sys.stdout))
LOG.propagate = False
COUPON_REALIZER = os.getenv('COUPON_REALIZER_URL', 'http://localhost:5002')


@blueprint.get('/<token>')
def validate_fan(token: str) -> Response:
    fan = models.FanApplication.from_token(token)
    if fan is None:
        LOG.warning('Token not found in DB')
        # TODO(perfa): log/return explanatory message (end-user facing)
        abort(HTTPStatus.BAD_REQUEST)

    discount = models.Discount.from_id(fan.discount_id)
    if discount is None:
        LOG.warning('Discount not found in DB')
        # TODO(perfa): log/return explanatory message (end-user facing)
        abort(HTTPStatus.BAD_REQUEST)

    coupon = Coupon.from_data(fan, discount)
    try:
        r = requests.post(COUPON_REALIZER + '/coupon', json=coupon.dict())
        r.raise_for_status()
    except HTTPError:
        LOG.warning('Failed to queue realization of coupon code.')
        abort(HTTPStatus.SERVICE_UNAVAILABLE)

    fan.delete()
    return 'OK'
