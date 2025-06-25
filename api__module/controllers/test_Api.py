import json

from odoo import http
from odoo.http import request


class TestApi(http.Controller):

    @http.route("/v1/post", methods=["POST"], type="http" , auth="none",csrf=False)
    def post_endpoint(self):
       args = request.httprequest.data.decode()
       vals = json.loads(args)
       print(vals)
