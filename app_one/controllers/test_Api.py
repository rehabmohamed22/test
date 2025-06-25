import json

from odoo import http
from odoo.http import request


class TestApi(http.Controller):

    @http.route("/v1/property", methods=["POST"], type="http" , auth="none",csrf=False)
    def post_endpoint(self):
       args = request.httprequest.data.decode()
       vals = json.loads(args)
       if not vals.get('name'):
           return request.make_json_response({
               "message": "Name is required",
           }, status=400)

       try:
            res = request.env['property'].sudo().create(vals)
            print(res)
            if res:
               return request.make_json_response({
                  "message": "Property has been created successfully",
                  "id": res.id,
                  "name": res.name
               } , status=201)
       except Exception as error:

           return request.make_json_response({
               "message": error,
           }, status=400)

    @http.route("/v1/property/json", methods=["POST"], type="json" , auth="none",csrf=False)
    def post_endpoint_json(self):
        args = request.httprequest.data.decode()
        vals = json.loads(args)
        res = request.env['property'].sudo().create(vals)
        if res:
            return {
                "message": "Property has been created successfully"

            }

    @http.route("/v1/property/<int:property_id>", methods=["PUT"], type="http", auth="none", csrf=False)
    def update_property(self,property_id):
      try:
        property_id = request.env['property'].sudo().search([('id' ,'=' , property_id)])
        if not property_id:
            return request.make_json_response({
                "message": "property id dose not exist!",
            }, status=400)

        print(property_id)
        args = request.httprequest.data.decode()
        vals = json.loads(args)
        print(vals)
        property_id.write(vals)
        print(property_id.garden_area)
        return request.make_json_response({
            "message": "Property has been updated successfully",
            "id": property_id.id,
            "name": property_id.name
        }, status=200)
      except Exception as error:

        return request.make_json_response({
            "message": error,
        }, status=400)








        