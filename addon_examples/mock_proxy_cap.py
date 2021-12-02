"""
Example of proxy-provided caps

Useful for mocking out a cap that isn't actually implemented by the server
while developing the viewer-side pieces of it.

Implements a cap that accepts an `obj_id` UUID query parameter and returns
the name of the object.
"""
import asyncio
import asgiref.wsgi

from flask import Flask, Response, request

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.proxy import addon_ctx
from hippolyzer.lib.proxy.webapp_cap_addon import WebAppCapAddon

app = Flask("GetObjectNameCapApp")


@app.route('/')
async def get_object_name():
    # Should always have the current region, the cap handler is bound to one.
    # Just need to pull it from the `addon_ctx` module's global.
    obj_mgr = addon_ctx.region.get().objects
    obj_id = UUID(request.args['obj_id'])
    obj = obj_mgr.lookup_fullid(obj_id)
    if not obj:
        return Response(f"Couldn't find {obj_id!r}", status=404, mimetype="text/plain")

    try:
        await asyncio.wait_for(obj_mgr.request_object_properties(obj)[0], 1.0)
    except asyncio.TimeoutError:
        return Response(f"Timed out requesting {obj_id!r}'s properties", status=500, mimetype="text/plain")

    return Response(obj.Name, mimetype="text/plain")


class MockProxyCapExampleAddon(WebAppCapAddon):
    # A cap URL with this name will be tied to each region when
    # the sim is first connected to. The URL will be returned to the
    # viewer in the Seed if the viewer requests it by name.
    CAP_NAME = "GetObjectNameExample"
    # Any asgi app should be fine.
    APP = asgiref.wsgi.WsgiToAsgi(app)


addons = [MockProxyCapExampleAddon()]
