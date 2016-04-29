from rest_framework.exceptions import ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from shielddash.api.forms import Form


class RetentionView(APIView):
    permission_classes = [IsAuthenticated]

    def perform_authentication(self, request):
        pass

    def get(self, request):
        form = Form(request.GET)
        if not form.is_valid():
            exc = ParseError()
            exc.detail = {'detail': dict(form.errors.items())}
            raise exc
        return Response({"study": "hello-world"})
