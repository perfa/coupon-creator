from sqlalchemy.sql import func

from .db import db


class Discount(db.Model):
    """A description of a brand's offered discount. Modelled loosely on WooCommerce/Shopify Coupon codes."""
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    __tablename__ = 'discounts'
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, nullable=False)  # Would be ForeignKey normally
    name = db.Column(db.String(50), nullable=False)
    fixed_code = db.Column(db.String(50))  # NULL == generate per-fan value
    date_created = db.Column(db.DateTime(timezone=True),
                             server_default=func.now())
    date_modified = db.Column(db.DateTime(timezone=True),
                              server_default=func.now())
    date_expires = db.Column(db.DateTime(timezone=True),
                             server_default=func.now())
    discount_type = db.Column(db.String(10), nullable=False)
    discount_amount = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    usage_limit = db.Column(db.Integer, nullable=False, default=1)
    free_shipping = db.Column(db.Boolean, nullable=False, default=False)
    verify_email = db.Column(db.Boolean, nullable=False, default=False)

    def save(self):
        db.session.add(self)
        db.session.commit()
