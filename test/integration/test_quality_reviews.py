__author__ = 'jasonrudland'

from datetime import datetime, timedelta


from lib.models import Review

import unittest

class MyTestCase(unittest.TestCase):

    global few_hours_ago, expected_review_providers
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
            is_complete = self.are_recent_reviews_complete(provider)
            if not is_complete :
                successCount -= 1
                print("Expected to find a complete reviews from the provider:" + provider)

        self.assertEqual(successCount, expectedCount, "Expected to find complete reviews for every provider today")


    def are_recent_reviews_complete(self, provider, has_rating=True, has_author=True,has_date=True, has_excerpt=True):

        reviews = Review.select().where(Review.provider == provider).where(Review.created_at > few_hours_ago)
        if has_rating:
            reviews = reviews.select().where(Review.rating > 0)

        if has_author:
            reviews = reviews.select().where(~(Review.author >> None)).where(Review.author.regexp(".{3,}"))

        if has_date:
            reviews = reviews.select().where(~(Review.date >> None)).where(Review.date.regexp("\D*\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d"))

        if has_excerpt:
            reviews = reviews.select().where(~(Review.excerpt >> None)).where(Review.excerpt.regexp(".{10,}"))

        return reviews.count() > 0


if __name__ == '__main__':
    unittest.main()
