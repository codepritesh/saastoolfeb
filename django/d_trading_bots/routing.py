from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import bs_sb_continuously_tool.routing
import two_way_sp.routing
import support_multi_box.routing
import arb_2way.routing
import atr_trailing_stop.routing
import atr_trailing_stop_tool.routing
import support_trailing_stop.routing
import support_big_amount.routing
import avg_tool.routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            bs_sb_continuously_tool.routing.websocket_urlpatterns +
            two_way_sp.routing.websocket_urlpatterns +
            support_multi_box.routing.websocket_urlpatterns +
            arb_2way.routing.websocket_urlpatterns +
            atr_trailing_stop.routing.websocket_urlpatterns +
            atr_trailing_stop_tool.routing.websocket_urlpatterns +
            support_trailing_stop.routing.websocket_urlpatterns +
            support_big_amount.routing.websocket_urlpatterns +
            avg_tool.routing.websocket_urlpatterns
        )
    ),
})
