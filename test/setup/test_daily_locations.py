__author__ = 'jasonrudland'

import json

import requests

from lib.sweetiq_api import SweetiqAPI

import unittest
from lib.models import Location


class MyTestCase(unittest.TestCase):

    global sweetiqApi
    sweetiqApi = SweetiqAPI(requests)

    def test_launch_location_runs(self):
        verified_cutoff= 0.7

        locations = [
            {"name":"Coast Victoria Harbourside Hotel","address":"146 Kingston St", "city":"Victoria", "province": "BC", "country" :"Canada", "postal":"V8V 1V4","phone":"(250) 360-1211"},
            {"name":"Ariadne Hair & Esthetics","address":"29 Crowfoot Rise", "city":"Calgary", "province": "AB","country" :"Canada",  "postal":"T3G 4P5","phone":"403-208-7355"},
            {"name":"Myth Games","address":"3434 34 Ave NE #4", "city":"Calgary", "province": "AB","country" :"Canada",  "postal":"T1Y 6X3","phone":"403-769-1909"},
            {"name":"Carol A Gogo","address":"16 Rue de la Gare", "city":"Saint-Sauveur-des-Monts", "province": "Quebec","country" :"Canada",  "postal":"J0R 1R0","phone":"450-227-8660"},
            {"name":"Frank's Pizza House","address":"1352 West St. Clair Avenue", "city":"Toronto", "province": "ON","country" :"Canada",  "postal":"M6E1C4","phone":"(416) 654-6554"}
        ]

        validation_weights = {
             "name": 1.0,
             "address": 1.0,
             "city": 0.2,
             "province": 0.3,
             "country": 1.0,
             "postal": 0.2,
             "phone": 1.0
         }

        for location_data in locations:
            self.launch_location_run(location_data, verified_cutoff, validation_weights)


    def launch_location_run(self, location_data, verified_cutoff=0.7, validation_weights = {}):

        result = sweetiqApi.run_location(location_data, "", verified_cutoff, validation_weights)

        self.assertFalse('success' not in result or not result['success'],'Failed to trigger run location request to sweetiQ API' + str(result))
        token_id = result['token_id']
        Location.create_location(token_id, location_data)
