__author__ = 'jasonrudland'

from datetime import datetime, timedelta


from lib.models import Listing

import unittest

class MyTestCase(unittest.TestCase):

    global few_hours_ago, expected_providers
    expected_providers = [
        "google",
        "bing",
        "yahoo",
        "yelp",
        "yellowpages",
        "411",
        "n49",
        "facebook",
        "foursquare",
        "tripadvisor",
        "urbanspoon",
        "restaurantica",
        "expedia",
        "canadaplus",
        "canpages",
        "dinehere",
        "canadianhotelguide",
        "lonelyplanet"
    ]

    few_hours_ago = datetime.now() - timedelta(hours=6)

    def test_listing_from_today_exist(self):

        successCount = expectedCount = len(expected_providers)
        for provider in expected_providers:
            is_complete = self.are_recent_listings_complete(provider)
            if not is_complete :
                successCount -= 1
                print("Expected to find a complete listing from the provider:" + provider)
        self.assertEqual(successCount, expectedCount, "Expected to find complete listings for every provider today")



    def are_recent_listings_complete(self, provider, has_name=True, has_address=True, has_phone=True, has_accuracy=True):

        listing = Listing.select().where(Listing.provider == provider).where(Listing.created_at > few_hours_ago)
        if listing.count() and has_name:
            listing = listing.select().where(Listing.name.regexp("\w{3,}"))

        if listing.count() and has_address:
            listing = listing.select().where(Listing.address.regexp(".*\w{4,}"))

        if listing.count() and has_phone:
            listing = listing.select().where(Listing.phone.regexp("\D*\d{3}.?\d\d.?\d\d"))

        if listing.count() and has_accuracy:
            listing = listing.select().where(Listing.accuracy >= 0.7)

        return listing.count() > 0

if __name__ == '__main__':
    unittest.main()
