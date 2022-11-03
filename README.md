Getting Started
===============
I recommend virtualenv and docker-compose to run and test this setup. For data storage the code uses sqlite, to create the database file and set up tables you can use Flask migrations.

```bash
virtualenv --python=python3.9 venv
. venv/bin/activate
pip3 install -r requirements-dev.txt
FLASK_APP=app.application:app APP_ENVIRONMENT=development flask db upgrade
```

At this point you can run `docker-compose up` and you can interact with the service on `localhost:5000`. All downstream services are mocked by a simple application that answers on all paths with `OK` and prints the METHOD, url and request body.

This service does create the coupon CODE, but does not intend to interface with all the services that might have such a coupon code registered, e.g. WooCommerce, Shopify, custom solutions or CRMs. This is queued with another service. Likewise, if an email must be verified through a sendout where the user clicks on an activation link, that service is assumed to be provided by an additional service.

API
===

 - GET /brands

    Return all the discounts registered across all brands (simply for visibility in this sandbox)

- POST /brands/&lt;brand&gt;/discounts

    Create a discount, a configuration for coupon codes either global (the same code for all recipients) or unique and per-user generated. Expected body is `DiscountDescription` in `app.data_types` (&lt;brand&gt; parameter ignored in this sandbox)

- PUT/DELETE /brands/&lt;brand&gt;/discounts/&lt;id&gt;

    Not implemented, but would be.

- POST /brands/&lt;brand&gt;/fans

    Register a "fan" of this band who wants to participate in this loyalty program. Expected body is `FanData` in `app.data_types`. Depending on whether our discount is set to verify email accounts or not, will either queue up a Coupon Code with a realization service (connected to WooCommerce et al based on Brand configuration) or request email validation through an email sendout service - in this case the fan data is stored with the activation token in a temporary table.

- GET /fans/&lt;token&gt;

    The "activation link" from the presumed email verification sendout. Matches our temporary data table and queues a Coupon Code if it is a match.


Example Calls (using HTTPie)
============================
Missing API token when interacting with brand endpoints
```
> http post localhost:5000/brands/test_brand/discounts name="new discount"

HTTP/1.1 401 UNAUTHORIZED
Access-Control-Allow-Origin: *
Connection: close
Content-Length: 317
Content-Type: text/html; charset=utf-8
Date: Thu, 03 Nov 2022 14:30:43 GMT
Server: Werkzeug/2.2.2 Python/3.9.13
...
```

Invalid POST to create a new discount
```
> http post localhost:5000/brands/test_brand/discounts X-API-Token:secret123 name="new discount"
HTTP/1.1 400 BAD REQUEST
Access-Control-Allow-Origin: *
Connection: close
Content-Length: 167
Content-Type: text/html; charset=utf-8
Date: Thu, 03 Nov 2022 15:05:20 GMT
Server: Werkzeug/2.2.2 Python/3.9.13
...
```

Valid POST to create a new discount
```
> http post localhost:5000/brands/test_brand/discounts X-API-Token:secret123 name="new discount" date_expires="2022-12-31" discount_type=PERCENT discount_amount=10

HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
Connection: close
Content-Length: 12
Content-Type: text/html; charset=utf-8
Date: Thu, 03 Nov 2022 15:03:51 GMT
Server: Werkzeug/2.2.2 Python/3.9.13

new discount
```

List discounts (this would of course not be an open GET in a real system, this is simply to get visibility into the DB)
```
> http localhost:5000/brands/
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
Connection: keep-alive
Content-Length: 334
Content-Type: application/json
Date: Thu, 03 Nov 2022 17:38:01 GMT
Server: gunicorn

[
    {
        "brand_id": 1234,
        "date_created": "Thu, 03 Nov 2022 17:37:27 GMT",
        "date_expires": "Sat, 31 Dec 2022 00:00:00 GMT",
        "date_modified": "Thu, 03 Nov 2022 17:37:27 GMT",
        "description": null,
        "discount_amount": 10,
        "discount_type": "PERCENT",
        "fixed_code": null,
        "free_shipping": false,
        "id": 1,
        "name": "new discount",
        "usage_limit": 1,
        "verify_email": false
    }
]
```

Register Fan data for discount that doesn't verify email
```
> http post localhost:5000/brands/test_brand/fans X-API-Token:secret123 name="Uni User" email="uu@example.com"
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
Connection: keep-alive
Content-Length: 2
Content-Type: text/html; charset=utf-8
Date: Thu, 03 Nov 2022 18:18:11 GMT
Server: gunicorn

OK

---

coupon-creator-mock_coupon_realizer-1  | POST coupon
coupon-creator-mock_coupon_realizer-1  | {
coupon-creator-mock_coupon_realizer-1  |   "fan_name": "Uni User",
coupon-creator-mock_coupon_realizer-1  |   "email": "uu@example.com",
coupon-creator-mock_coupon_realizer-1  |   "facebook_handle": null,
coupon-creator-mock_coupon_realizer-1  |   "discount_name": "new discount",
coupon-creator-mock_coupon_realizer-1  |   "coupon_code": "ec23d8fe61de428e8493a7ed1acffbb9",
coupon-creator-mock_coupon_realizer-1  |   "discount_type": "PERCENT",
coupon-creator-mock_coupon_realizer-1  |   "discount_amount": 10,
coupon-creator-mock_coupon_realizer-1  |   "description": null,
coupon-creator-mock_coupon_realizer-1  |   "usage_limit": 1,
coupon-creator-mock_coupon_realizer-1  |   "free_shipping": false
coupon-creator-mock_coupon_realizer-1  | }
```

Register Fan data for discount that requires email verification (email sent to account and link clicked to verify)
```
> http post localhost:5000/brands/test_brand/fans X-API-Token:secret123 name="Uni User" email="uu@example.com"
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
Connection: keep-alive
Content-Length: 2
Content-Type: text/html; charset=utf-8
Date: Thu, 03 Nov 2022 18:28:42 GMT
Server: gunicorn

OK

---

coupon-creator-mock_email_verifier-1   | POST email
coupon-creator-mock_email_verifier-1   | {
coupon-creator-mock_email_verifier-1   |   "email": "uu@example.com",
coupon-creator-mock_email_verifier-1   |   "token": "8df2481c04694c31ac36bda5e5e349ba",
coupon-creator-mock_email_verifier-1   |   "brand": 1234
coupon-creator-mock_email_verifier-1   | }
```

Activate coupon for verified email
```
> http localhost:5000/fans/8df2481c04694c31ac36bda5e5e349ba
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
Connection: keep-alive
Content-Length: 2
Content-Type: text/html; charset=utf-8
Date: Thu, 03 Nov 2022 18:43:25 GMT
Server: gunicorn

OK

---

coupon-creator-mock_coupon_realizer-1  | POST coupon
coupon-creator-mock_coupon_realizer-1  | {
coupon-creator-mock_coupon_realizer-1  |   "fan_name": "Uni User",
coupon-creator-mock_coupon_realizer-1  |   "email": "uu@example.com",
coupon-creator-mock_coupon_realizer-1  |   "facebook_handle": null,
coupon-creator-mock_coupon_realizer-1  |   "discount_name": "verified discount",
coupon-creator-mock_coupon_realizer-1  |   "coupon_code": "0603a4f713da4f8ea602415d2e455bfa",
coupon-creator-mock_coupon_realizer-1  |   "discount_type": "PERCENT",
coupon-creator-mock_coupon_realizer-1  |   "discount_amount": 12,
coupon-creator-mock_coupon_realizer-1  |   "description": null,
coupon-creator-mock_coupon_realizer-1  |   "usage_limit": 1,
coupon-creator-mock_coupon_realizer-1  |   "free_shipping": false
coupon-creator-mock_coupon_realizer-1  | }
```
