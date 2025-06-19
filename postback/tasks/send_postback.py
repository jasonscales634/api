import requests
from project._celery import _celery
from ..models import Postback, Log


def find_postbacks(affiliate_id, offer_id=None):
    filters = {'affiliate_id': affiliate_id}
    if offer_id:
        filters['offer_id'] = offer_id
    return Postback.objects.filter(**filters)


@_celery.task
def send_postback(conversion):
    assert conversion.get('offer_id'), "Missing offer_id"
    assert conversion.get('affiliate_id'), "Missing affiliate_id"

    offer_id = conversion['offer_id']
    affiliate_id = conversion['affiliate_id']

    # Step 1: Try offer-specific postbacks first
    postbacks = find_postbacks(affiliate_id=affiliate_id, offer_id=offer_id)

    # Step 2: Fallback to general postbacks (no offer filter)
    if not postbacks.exists():
        postbacks = find_postbacks(affiliate_id=affiliate_id)

    # Step 3: Loop through each valid postback
    for postback in postbacks:
        if postback.goal and postback.goal != conversion.get('goal_value'):
            continue

        url = replace_macro(postback.url, conversion)

        try:
            resp = requests.get(url, timeout=5)
            persist_log(affiliate_id, url, str(resp.status_code), resp.text)
        except requests.exceptions.Timeout:
            persist_log(affiliate_id, url, '', 'Timeout')
        except Exception as e:
            persist_log(affiliate_id, url, '', str(e))


def replace_macro(url: str, data: dict) -> str:
    macros = {
        '{sub1}': data.get('sub1', ''),
        '{sub2}': data.get('sub2', ''),
        '{sub3}': data.get('sub3', ''),
        '{sub4}': data.get('sub4', ''),
        '{sub5}': data.get('sub5', ''),
        '{offer}': str(data.get('offer_id', '')),
        '{sum}': str(data.get('payout', '')),
        '{currency}': data.get('currency') or '',
        '{goal}': data.get('goal_value', ''),
    }

    for macro, value in macros.items():
        url = url.replace(macro, value)

    return url


def persist_log(affiliate_id: int, url: str, status: str, text: str):
    Log.objects.create(
        affiliate_id=affiliate_id,
        url=url,
        response_status=status,
        response_text=text
    )
