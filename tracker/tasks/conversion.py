from project._celery import _celery
from tracker.models import Click, Conversion, HOLD_STATUS, REJECTED_STATUS
from offer.models import Payout

@_celery.task
def conversion(data):
    try:
        click = Click.objects.get(pk=data['click_id'])
    except Click.DoesNotExist:
        return f"❌ Click not found: {data['click_id']}"

    # Check if conversion already exists for the same click+goal
    existing = Conversion.objects.filter(click_id=click.id, goal_value=data['goal']).first()
    if existing and data.get('status') and existing.status == HOLD_STATUS:
        existing.status = data['status']
        existing.save()
        return f"✅ Conversion updated: {click.id}"

    duplicate = bool(existing)

    # Payout info
    payout = Payout.objects.filter(
        offer_id=click.offer_id,
        goal_value=data['goal'],
        countries__in=[click.country]
    ).first()

    # Create Conversion
    conv = Conversion(
        click=click,
        click_date=click.created_at,
        offer=click.offer,
        affiliate=click.affiliate,
        affiliate_manager=click.affiliate.profile.manager if click.affiliate and hasattr(click.affiliate, 'profile') else None,

        sub1=click.sub1,
        sub2=click.sub2,
        sub3=click.sub3,
        sub4=click.sub4,
        sub5=click.sub5,

        ip=click.ip,
        country=click.country,
        city=getattr(click, 'city', ''),  # ✅ only if city field exists
        isp=getattr(click, 'isp', ''),    # ✅ added ISP field support
        ua=click.ua,
        os=click.os,
        device=click.device,
        device_time=click.device_time,
        ip_local_time=click.ip_local_time,

        goal_value=data['goal'],
        sum=data['sum'],
        status=HOLD_STATUS,
    )

    if payout:
        conv.revenue = payout.revenue
        conv.payout = payout.payout
        conv.goal = payout.goal
        conv.currency = payout.currency

        if data.get('status'):
            conv.status = data['status']
        if duplicate:
            conv.status = REJECTED_STATUS
            conv.comment = 'Duplicate Click ID'
    else:
        conv.revenue = 0
        conv.payout = 0
        conv.status = REJECTED_STATUS
        conv.comment = 'Payout not found'

    conv.save()
    return f"✅ Conversion saved: {conv.id}"
