__author__ = 'jasonrudland'

from datetime import datetime, timedelta


from lib.models import Listing

import unittest

class MyTestCase(unittest.TestCase):

    global few_hours_ago, expected_providers, expected_listings_without_phone
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
        "canpages",
        "dinehere",
        "canadianhotelguide",
    ]

    expected_listings_without_phone = [
        "lonelyplanet"
    ]
    # unsearchable: Oct 31, 2014    "canadaplus",

    few_hours_ago = datetime.now() - timedelta(hours=6)

    def test_listing_from_today_exist(self):

        successCount = expectedCount = len(expected_providers)
        actual_failed_listings = []
        for provider in expected_providers:
            is_complete = self.are_recent_listings_complete(provider)
            if not is_complete :
                successCount -= 1
                actual_failed_listings.append(provider)
                print("Expected to find a complete listing from the provider:" + provider)
        self.assertEqual(successCount, expectedCount, "Expected to find complete listings for every provider today:" + ",".join(actual_failed_listings))

    def test_listing_from_today_without_phone(self):

        successCount = expectedCount = len(expected_listings_without_phone)
        actual_failed_listings = []
        for provider in expected_listings_without_phone:
            is_complete = self.are_recent_listings_complete(provider, True, True, False)
            if not is_complete :
                successCount -= 1
                actual_failed_listings.append(provider)
                print("Expected to find a listing without the phone number from the provider:" + provider)
        self.assertEqual(successCount, expectedCount, "Expected to find listings without phone numbers for the providers:" + ",".join(actual_failed_listings))


    def test_ensure_listing_from_today_have_no_phone(self):

        successCount = expectedCount = len(expected_listings_without_phone)
        actual_failed_listings = []
        for provider in expected_listings_without_phone:
            is_missing_field = self.recent_listings_have_missing_field(provider, True, True, False)
            if not is_missing_field :
                successCount -= 1
                actual_failed_listings.append(provider)
                print("Expected to find all listing have no phone number from the provider:" + provider)
        self.assertEqual(successCount, expectedCount, "Expected to find all listing have no phone numbers for the providers:" + ",".join(actual_failed_listings))



    def are_recent_listings_complete(self, provider, has_name=True, has_address=True, has_phone=True, has_accuracy=True):

        listing = Listing.select().where(Listing.provider == provider).where(Listing.created_at > few_hours_ago)

        if has_name:
            listing = listing.select().where(~(Listing.name >> None)).where(Listing.name.regexp("\w{3,}"))

        if has_address:
            listing = listing.select().where(~(Listing.address >> None)).where(Listing.address.regexp(".*\w{4,}"))

        if has_phone:
            listing = listing.select().where(~(Listing.phone >> None)).where(Listing.phone.regexp("\D*\d{3}.?\d\d.?\d\d"))

        if has_accuracy:
            listing = listing.select().where(Listing.accuracy >= 0.5)

        return listing.count() > 0

    def recent_listings_have_missing_field(self, provider, has_no_name=False, has_no_address=False, has_no_phone=False, has_no_accuracy=False):

        listing = Listing.select().where(Listing.provider == provider).where(Listing.created_at > few_hours_ago)

        if has_no_name:
            listing = listing.select().where(~(Listing.name))

        if has_no_address:
            listing = listing.select().where(~(Listing.address))

        if has_no_phone:
            listing = listing.select().where(~(Listing.phone))

        if has_no_accuracy:
            listing = listing.select().where(~(Listing.accuracy))

        return listing.count() == 0

if __name__ == '__main__':
    unittest.main()
