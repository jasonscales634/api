from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator
from tracker.models import Click  # ✅ Ensure correct import

class ClickListAPIView(APIView):
    def get(self, request):
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))

        # ✅ Admin sees all, Affiliate sees own data
        if request.user.is_staff or request.user.is_superuser:
            clicks = Click.objects.all().order_by('-created_at')
        else:
            clicks = Click.objects.filter(affiliate=request.user).order_by('-created_at')

        paginator = Paginator(clicks, per_page)
        page_obj = paginator.get_page(page)

        data = []
        for click in page_obj:
            data.append({
                "id": str(click.id),
                "ip": click.ip,
                "ua": click.ua,
                "country": click.country,
                "city": "",  # Optional
                "device": click.device,
                "os": click.os,
                "browser": click.browser,
                "referrer": "",
                "sub1": click.sub1 or "",
                "sub2": click.sub2 or "",
                "sub3": click.sub3 or "",
                "sub4": click.sub4 or "",
                "sub5": click.sub5 or "",
                "offer": {
                    "id": click.offer.id if click.offer else None,
                    "offer_id": "",  # If applicable
                    "title": click.offer.title if click.offer else ""
                },
                "conversion_id": "",
                "ios_idfa": click.ios_idfa or "",
                "android_id": click.android_id or "",
                "created_at": click.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "uniq": int(click.uniq),
                "cbid": click.cbid,
                "partner_id": click.affiliate_id,
            })

        return Response({
            "status": 1,
            "clicks": data,
            "pagination": {
                "per_page": per_page,
                "total_count": paginator.count,
                "page": page
            }
        })
