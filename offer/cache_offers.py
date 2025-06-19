from offer.models import Offer
import logging

logger = logging.getLogger(__name__)


class TrackerCache:
    _offer_cache = {}

    @classmethod
    def get_offer(cls, offer_id):
        if offer_id in cls._offer_cache:
            return cls._offer_cache[offer_id]

        try:
            offer = Offer.objects.filter(id=offer_id, status='active').values(
                'id', 'title', 'tracking_template', 'url', 'status', 'payout', 'revenue'
            ).first()

            if offer:
                # ✅ tracking_template না থাকলে fallback হিসেবে url ব্যবহার করো
                tracking_template = offer.pop('tracking_template', '') or ''
                if not tracking_template and offer.get('url'):
                    logger.warning(f"⚠️ tracking_template missing for Offer ID {offer_id}, using url as fallback.")
                    tracking_template = offer['url']

                offer['tracking_link'] = tracking_template

            else:
                logger.warning(f"❌ Offer ID {offer_id} not found or inactive.")

            cls._offer_cache[offer_id] = offer
            return offer

        except Exception as e:
            logger.error(f"🔥 Failed to fetch offer {offer_id}: {e}")
            return None

    @classmethod
    def clear_cache(cls):
        cls._offer_cache.clear()
        logger.info("✅ TrackerCache cleared.")
