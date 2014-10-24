__author__ = 'jasonrudland'

import json

import requests

from lib.sweetiq_api import SweetiqAPI

import unittest

class MyTestCase(unittest.TestCase):

    global sweetiqApi
    sweetiqApi = SweetiqAPI(requests)

    def test_launch_location_runs(self):
        verified_cutoff= 0.7

        locations = [
            {"name":"Lasik MD","address":"1801 Hollis Street Suite 400", "city":"Halifax", "province": "NS", "country" :"Canada", "postal":"B3J3N4","phone":"1-902-4425050"},
            {"name":"Ariadne Hair & Esthetics","address":"29 Crowfoot Rise", "city":"Calgary", "province": "AB","country" :"Canada",  "postal":"T3G 4P5","phone":"403-208-7355"},
            {"name":"Myth Games","address":"3434 34 Ave NE #4", "city":"Calgary", "province": "AB","country" :"Canada",  "postal":"T1Y 6X3","phone":"403-769-1909"},
            {"name":"Carol A Gogo","address":"16 Rue de la Gare", "city":"Saint-Sauveur-des-Monts", "province": "Quebec","country" :"Canada",  "postal":"J0R 1R0","phone":"450-227-8660"},
            {"name":"Union Oyster House","address":"41 Union St", "city":"Boston", "province": "MA","country" :"United States",  "postal":"02108","phone":"(617) 227-2750"}
        ]


        for location_data in locations:
            self.launch_location_run(location_data, verified_cutoff)


    def launch_location_run(self, location_data, verified_cutoff=0.7):

        result = sweetiqApi.run_location(location_data, "", verified_cutoff)

        self.assertFalse('success' not in result or not result['success'],'Failed to trigger run location request to sweetiQ API')