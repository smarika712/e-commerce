import hmac
import hashlib
import base64
from django.conf import settings


def generate_esewa_signature(total_amount, transaction_uuid, product_code=None):
    product_code = product_code or settings.ESEWA_PRODUCT_CODE
    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    hmac_obj = hmac.new(
        settings.ESEWA_SECRET_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    )
    return base64.b64encode(hmac_obj.digest()).decode('utf-8')


def verify_esewa_signature(data: dict):
    signed_field_names = data.get('signed_field_names', '').split(',')
    message = ",".join(f"{field}={data.get(field, '')}" for field in signed_field_names)
    hmac_obj = hmac.new(
        settings.ESEWA_SECRET_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    )
    signature = base64.b64encode(hmac_obj.digest()).decode('utf-8')
    return hmac.compare_digest(signature, data.get('signature', ''))