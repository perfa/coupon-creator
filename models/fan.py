from sqlalchemy.sql import func

from .db import db


class FanApplication(db.Model):
    """A holding table for fans' data when verify email through email->validation link->url-with-token loop.
    Here lie privacy issues, GDPR notification requirements et al."""
    __tablename__ = 'fan_applications'
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, nullable=False)  # Would be ForeignKey normally
    discount_id = db.Column(db.Integer, db.ForeignKey('discounts.id'), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True),
                             server_default=func.now())
    token = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    facebook_handle = db.Column(db.String(50))
    # ... and so on

    @classmethod
    def from_token(cls, token: str) -> 'FanApplication':
        return db.session.query(FanApplication).filter(FanApplication.token == token).one_or_none()
