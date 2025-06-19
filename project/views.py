from django.http import HttpResponse, HttpRequest
from django.shortcuts import redirect, get_object_or_404
from tracker.models import Click

def home_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("🎯 ADCpa Tracker Server is Live")

def redirect_view(request: HttpRequest) -> HttpResponse:
    click_id = request.GET.get("click_id")
    if not click_id:
        return HttpResponse("❌ click_id লাগবে", status=400)

    click = get_object_or_404(Click, id=click_id)

    if not click.offer:
        return HttpResponse("❌ অফার পাওয়া যায়নি", status=404)

    tracking_link = click.offer.get_tracking_url(
        click_id=click.id,
        pid=click.affiliate.id if click.affiliate else '',
        sub1=click.sub1,
        sub2=click.sub2,
        sub3=click.sub3,
        sub4=click.sub4,
        sub5=click.sub5
    )

    if not tracking_link:
        return HttpResponse("❌ অফারের ট্র্যাকিং লিংক ফাঁকা", status=404)

    return redirect(tracking_link)
