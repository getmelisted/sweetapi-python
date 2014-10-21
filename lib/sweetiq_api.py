import json

__author__ = 'pat'

import config



# Made into a class so we can test with a mock implementation of request
class SweetiqAPI:
    def __init__(self, requests):
        self.requests = requests

    def run_location(self, location_data, account_api_key, verified_cutoff):
        url = '%s%s?api_key=%s&verified_cutoff=%s' % (config.sweetiq_api_url, 'presence-api', account_api_key or config.sweetiq_api_key, verified_cutoff)
        payload = {
            'location': json.dumps(location_data),
            'listing_callback_url': config.sweetiq_api_listing_callback_url,
            'review_callback_url': config.sweetiq_api_review_callback_url,
            'completed_callback_url': config.sweetiq_api_completed_callback_url
        }

        r = self.requests.get(url, params=payload, verify=False)
        return r.json()