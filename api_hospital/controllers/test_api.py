from odoo import http
from odoo.http import route


class TestApi(http.Controller):

    @http.route("/api2/test",methods=["GET"],type="http" ,auth="none" ,csrf=False)
    def test_endpoint(self):
        print('inside test_endpoint')


