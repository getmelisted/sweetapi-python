__author__ = 'jasonrudland'

from datetime import datetime, timedelta


from lib.models import Location, Listing, Review

import unittest

class MyTestCase(unittest.TestCase):

    global few_hours_ago, expected_providers,expected_review_providers
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

    expected_review_providers = [
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


    def test_reviews_from_today_exist(self):

        successCount = expectedCount = len(expected_review_providers)
        for provider in expected_review_providers:
            reviews = Review.select().where(Review.provider == provider).where(Review.created_at > few_hours_ago)
            if not reviews.count() :
                successCount -= 1
                print("Expected to find a review from the provider:" + provider)
        self.assertEqual(successCount, expectedCount, "Expected to find all providers in the reviews for today.")

    def test_listing_from_today_exist(self):

        successCount = expectedCount = len(expected_providers)
        for provider in expected_providers:
            listings = Listing.select().where(Listing.provider == provider).where(Listing.created_at > few_hours_ago )
            if not listings.count() :
                successCount -= 1
                print("Expected to find a listing from the provider:" + provider)
        self.assertEqual(successCount, expectedCount, "Expected to find all providers in the listings for today")


if __name__ == '__main__':
    unittest.main()
