import hmac
import hashlib
import base64

# eSewa TEST credentials (UAT). Replace with your real merchant code/secret in production.
ESEWA_PRODUCT_CODE = "EPAYTEST"
ESEWA_SECRET_KEY = "8gBm/:&EnhH.1/q"
ESEWA_FORM_URL = "https://rc-epay.esewa.com.np/api/epay/main/v2/form"


def generate_esewa_signature(total_amount, transaction_uuid, product_code=ESEWA_PRODUCT_CODE, secret_key=ESEWA_SECRET_KEY):
    """
    eSewa signs a fixed message string built from these three fields,
    in this exact order, using HMAC-SHA256, then base64-encodes the result.
    """
    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    hmac_obj = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    )
    return base64.b64encode(hmac_obj.digest()).decode('utf-8')


def verify_esewa_signature(data: dict, secret_key=ESEWA_SECRET_KEY):
    """
    Verifies the signature eSewa sends back in the callback response.
    'data' is the decoded JSON dict from the base64 response.
    """
    signed_field_names = data.get('signed_field_names', '').split(',')
    message = ",".join(f"{field}={data.get(field, '')}" for field in signed_field_names)

    hmac_obj = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    )
    signature = base64.b64encode(hmac_obj.digest()).decode('utf-8')

    return hmac.compare_digest(signature, data.get('signature', ''))