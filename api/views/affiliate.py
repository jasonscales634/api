from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from affiliate.serializers import RegisterAffiliateSerializer


@api_view(['POST', 'GET'])
def affiliate_register(request):
    serializer = RegisterAffiliateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "✅ Registration successful"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
