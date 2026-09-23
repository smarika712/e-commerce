import requests
from django.conf import settings


def initiate_khalti_payment(
    amount,
    purchase_order_id,
    purchase_order_name,
    return_url,
    website_url,
    customer_name,
    customer_email,
    customer_phone,
):
    payload = {
        "return_url": return_url,
        "website_url": website_url,
        "amount": int(round(float(amount) * 100)),
        "purchase_order_id": purchase_order_id,
        "purchase_order_name": purchase_order_name,
        "customer_info": {
            "name": customer_name,
            "email": customer_email,
            "phone": customer_phone,
        },
    }

    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        settings.KHALTI_PAYMENT_URL,
        json=payload,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def lookup_khalti_payment(pidx):

    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        settings.KHALTI_LOOKUP_URL,
        json={"pidx": pidx},
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()