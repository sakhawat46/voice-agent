# from django.conf import settings
# import requests
# from rest_framework import viewsets, status
# from rest_framework.decorators import api_view
# from rest_framework.permissions import IsAuthenticatedOrReadOnly
# from rest_framework.response import Response
# from .models import Agent
# from .serializers import AgentSerializer

# OPENAI_API_KEY = settings.OPENAI_API_KEY

# REALTIME_SESSION_URL = "https://api.openai.com/v1/realtime/sessions"
# CHAT_URL = "https://api.openai.com/v1/chat/completions"



# class AgentViewSet(viewsets.ModelViewSet):
#     queryset = Agent.objects.all().order_by('-updated_at')
#     serializer_class = AgentSerializer
#     permission_classes = [IsAuthenticatedOrReadOnly]


# @api_view(["POST"])
# def agent_chat(request, pk):
#     """
#     Body: {"message": "আজ কি খোলা?"}
#     Text chat test: agent_prompt + business_details inject করা হচ্ছে।
#     """
#     try:
#         agent = Agent.objects.get(pk=pk, enabled=True)
#     except Agent.DoesNotExist:
#         return Response({"detail": "Agent not found"}, status=404)

#     user_msg = request.data.get("message", "")

#     system = agent.agent_prompt or "You are a helpful Bengali assistant."
#     business_blob = f"Business details (JSON): {agent.business_details}"

#     payload = {
#         "model": "gpt-4o-mini",
#         "messages": [
#             {"role": "system", "content": system},
#             {"role": "system", "content": business_blob},
#             {"role": "user", "content": user_msg},
#         ],
#     }

#     r = requests.post(
#         CHAT_URL,
#         headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
#         json=payload,
#         timeout=30,
#     )
#     if r.status_code >= 400:
#         return Response({"error": r.text}, status=r.status_code)

#     data = r.json()
#     reply = data["choices"][0]["message"]["content"]
#     return Response({"reply": reply}, status=200)

# @api_view(["POST"])
# def create_realtime_token(request):
#     agent_id = request.data.get("agent_id")
#     if not OPENAI_API_KEY:
#         return Response({"error":"OPENAI_API_KEY missing"}, status=500)

#     try:
#         agent = Agent.objects.get(id=agent_id, enabled=True)
#     except Agent.DoesNotExist:
#         return Response({"detail":"Agent not found or disabled."}, status=404)

#     payload = {
#         "model": "gpt-realtime",              # ✅ GA realtime model
#         "instructions": agent.agent_prompt,   # ✅ system prompt
#         # "voice": agent.voice,               # optional; test without if error persists
#     }

#     try:
#         r = requests.post(
#             REALTIME_SESSION_URL,
#             headers={
#                 "Authorization": f"Bearer {OPENAI_API_KEY}",
#                 "Content-Type": "application/json",
#             },
#             json=payload, timeout=20
#         )
#     except requests.RequestException as e:
#         return Response({"error": f"Upstream request failed: {e}"}, status=502)

#     if r.status_code >= 400:
#         # ডিবাগিংয়ের সুবিধার জন্য আপস্ট্রিম বডি ফিরিয়ে দেই
#         return Response({"error":"Upstream error creating realtime session",
#                          "status": r.status_code, "body": r.text}, status=r.status_code)

#     data = r.json()
#     ek = (data.get("client_secret") or {}).get("value") or data.get("value")
#     if not ek:
#         return Response({"error":"No ek in upstream response", "upstream": data}, status=502)

#     return Response({"value": ek, "expires_at": (data.get("client_secret") or {}).get("expires_at")}, status=200)









# agentapp/views.py
from django.conf import settings
import requests
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import Agent
from .serializers import AgentSerializer

OPENAI_API_KEY = settings.OPENAI_API_KEY
REALTIME_SESSION_URL = "https://api.openai.com/v1/realtime/sessions"
CHAT_URL = "https://api.openai.com/v1/chat/completions"


class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all().order_by('-updated_at')
    serializer_class = AgentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class AgentChatView(APIView):
    """
    POST /api/agents/<pk>/chat/
    Body: {"message": "..."}
    Text chat test: agent_prompt + business_details ইনজেক্ট করা হয়।
    """
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, pk):
        try:
            agent = Agent.objects.get(pk=pk, enabled=True)
        except Agent.DoesNotExist:
            return Response({"detail": "Agent not found"}, status=status.HTTP_404_NOT_FOUND)

        user_msg = request.data.get("message", "")
        system = agent.agent_prompt or "You are a helpful Bengali assistant."
        business_blob = f"Business details (JSON): {agent.business_details}"

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system},
                {"role": "system", "content": business_blob},
                {"role": "user", "content": user_msg},
            ],
        }

        try:
            r = requests.post(
                CHAT_URL,
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                json=payload,
                timeout=30,
            )
        except requests.RequestException as e:
            return Response({"error": f"Upstream request failed: {e}"}, status=status.HTTP_502_BAD_GATEWAY)

        if r.status_code >= 400:
            return Response({"error": r.text}, status=r.status_code)

        data = r.json()
        reply = data["choices"][0]["message"]["content"]
        return Response({"reply": reply}, status=status.HTTP_200_OK)


class RealtimeTokenView(APIView):
    """
    POST /api/realtime/token/
    Body: {"agent_id": 1}
    WebRTC ব্রাউজারের জন্য short-lived ephemeral key (ek_...) তৈরি করে।
    """
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        agent_id = request.data.get("agent_id")

        if not OPENAI_API_KEY:
            return Response({"error": "OPENAI_API_KEY missing"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            agent = Agent.objects.get(id=agent_id, enabled=True)
        except Agent.DoesNotExist:
            return Response({"detail": "Agent not found or disabled."}, status=status.HTTP_404_NOT_FOUND)

        # মিনিমাল, সেফ পেলোড রাখি—মডেল GA 'gpt-realtime'
        payload = {
            "model": "gpt-realtime",
            "instructions": agent.agent_prompt,
            # "voice": agent.voice,  # চাইলে পরে যোগ করুন; প্রথমে বাদ দিয়ে টেস্ট করা ভাল
        }

        try:
            r = requests.post(
                REALTIME_SESSION_URL,
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=20,
            )
        except requests.RequestException as e:
            return Response({"error": f"Upstream request failed: {e}"}, status=status.HTTP_502_BAD_GATEWAY)

        if r.status_code >= 400:
            # ডিবাগিংয়ের সুবিধার জন্য আপস্ট্রিম বডি ফিরিয়ে দিই
            return Response(
                {"error": "Upstream error creating realtime session",
                 "status": r.status_code, "body": r.text},
                status=r.status_code
            )

        data = r.json()
        ek = (data.get("client_secret") or {}).get("value") or data.get("value")
        expires_at = (data.get("client_secret") or {}).get("expires_at")

        if not ek:
            return Response({"error": "No ek in upstream response", "upstream": data}, status=status.HTTP_502_BAD_GATEWAY)

        # ফ্রন্টএন্ড সহজ রাখতে টপ-লেভেলে value রিটার্ন
        return Response({"value": ek, "expires_at": expires_at}, status=status.HTTP_200_OK)
