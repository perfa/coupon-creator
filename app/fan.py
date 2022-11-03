from http import HTTPStatus
from typing import Optional

from flask import Blueprint, Response, abort
from pydantic import BaseModel

import models

blueprint = Blueprint('fans', __name__)


class FanDescription(BaseModel):
    name: str
    email: str
    facebook_handle: Optional[str]


@blueprint.get('/<fan_token>')
def validate_fan(fan_token: str) -> Response:
    fan_data = models.FanApplication.for_token(fan_token)
    if fan_data is None:
        abort(HTTPStatus.BAD_REQUEST)

    return 'OK'
