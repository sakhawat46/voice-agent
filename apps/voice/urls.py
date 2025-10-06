# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import AgentViewSet, agent_chat, create_realtime_token

# router = DefaultRouter()
# router.register(r"api/agents", AgentViewSet, basename="agent")

# urlpatterns = [
#     path("", include(router.urls)),
#     path("api/agents/<int:pk>/chat/", agent_chat),
#     path("api/realtime/token/", create_realtime_token),
# ]







# agentapp/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AgentViewSet, AgentChatView, RealtimeTokenView

router = DefaultRouter()
router.register(r"api/agents", AgentViewSet, basename="agent")

urlpatterns = [
    path("", include(router.urls)),
    path("api/agents/<int:pk>/chat/", AgentChatView.as_view()),
    path("api/realtime/token/", RealtimeTokenView.as_view()),
]
