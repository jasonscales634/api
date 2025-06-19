import logging
import ipaddress
from django.contrib.auth import get_user_model
from project._celery import _celery
from tracker.models import Click
from ext.ipapi import API, Err as IpstackErr
from tracker.utils import get_device_info, get_geo_time
from geolite2 import geolite2
from django.utils.dateparse import parse_datetime

logger = logging.getLogger(__name__)
reader = geolite2.reader()

User = get_user_model()


def is_valid_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def get_ip_data(ip: str):
    api = API()
    try:
        return api.query(ip)
    except IpstackErr as e:
        logger.warning(f"Ipstack error for IP {ip}: {e}")
        return None


def detect_country(ip: str) -> str:
    ip_info = reader.get(ip) or {}
    return ip_info.get("country", {}).get("iso_code", "") or ""


def detect_city(ip: str) -> str:
    ip_info = reader.get(ip) or {}
    return ip_info.get("city", {}).get("names", {}).get("en", "") or ""


@_celery.task
def click(data):
    try:
        ip = data.get("ip", "")
        if not is_valid_ip(ip):
            logger.warning(f"❌ Invalid IP: {ip}")
            return f"Invalid IP: {ip}"

        # Geo Info
        geo = get_ip_data(ip)
        country = geo.country_code if geo and geo.country_code else detect_country(ip)
        city = geo.city if geo and geo.city else detect_city(ip)
        isp = (geo.org or geo.isp) if geo else ''

        # User
        user = User.objects.get(pk=data["pid"])

        # Device Info
        device_info = get_device_info(data["ua"])
        os = device_info.get("os")
        device = device_info.get("device")

        # Time
        device_time = parse_datetime(data.get("device_time")) if data.get("device_time") else None
        ip_local_time = get_geo_time(ip)

        # Host (optional if passed)
        host = data.get("host", "")

        # Save Click
        click = Click(
            id=data["click_id"],
            offer_id=data["offer_id"],
            affiliate_id=data["pid"],
            affiliate_manager=user.profile.manager,
            sub1=data.get("sub1", ""),
            sub2=data.get("sub2", ""),
            sub3=data.get("sub3", ""),
            sub4=data.get("sub4", ""),
            sub5=data.get("sub5", ""),
            revenue=0,
            payout=0,
            ip=ip,
            country=country,
            city=city,
            isp=isp,
            ua=data["ua"],
            os=os,
            device=device,
            device_time=device_time,
            ip_local_time=ip_local_time,
            host=host  # Make sure this field exists in your Click model
        )
        click.save()

        logger.info(f"✅ Click created: {click.id}")
        return f"Click created: {click.id}"

    except User.DoesNotExist:
        logger.error(f"❌ Affiliate not found: {data.get('pid')}")
        return f"Affiliate not found: {data.get('pid')}"

    except Exception as e:
        logger.exception(f"❌ Failed to create Click: {e}")
        return f"Failed to create Click: {e}"


