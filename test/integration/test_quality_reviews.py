__author__ = 'jasonrudland'

from datetime import datetime, timedelta


from lib.models import Review

import unittest

class MyTestCase(unittest.TestCase):

    global few_hours_ago, expected_review_providers, expected_without_ratings, expected_without_author
    expected_review_providers = [
        "google",
        "yahoo",
        "yelp",
        "yellowpages",
        "411",
        "n49",
        "facebook",
        "tripadvisor",
        "urbanspoon",
        "restaurantica",
        "expedia",
        "canpages",
        "dinehere",
        "canadianhotelguide",
    ]
    # unsearchable: Oct 31, 2014    "canadaplus",
    # No reviews "lonelyplanet"

    expected_without_ratings = [
        "foursquare",
    ]

    expected_without_author = [
        "bing",
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

    def test_reviews_from_today_without_ratings_exist(self):
        successCount = expectedCount = len(expected_without_ratings)
        for provider in expected_without_ratings:
            is_complete = self.are_recent_reviews_complete(provider, False)
            if not is_complete :
                successCount -= 1
                print("Expected to find a complete reviews without ratings from the provider:" + provider)

        self.assertEqual(successCount, expectedCount, "Expected to find reviews just without ratings for : " + ", ".join(expected_without_ratings))

    def test_ensure_all_reviews_from_today_without_ratings(self):
        successCount = expectedCount = len(expected_without_ratings)
        actual_failed_providers = []
        for provider in expected_without_ratings:
            is_missing = self.recent_reviews_are_missing_field(provider, True)
            if not is_missing :
                actual_failed_providers.append(provider)
                successCount -= 1
                print("Expected to find all reviews without ratings from the provider:" + provider)

        self.assertEqual(successCount, expectedCount, "Expected to find all reviews without ratings for : " + ", ".join(actual_failed_providers))

    def test_reviews_from_today_without_author_exist(self):
        successCount = expectedCount = len(expected_without_author)
        for provider in expected_without_author:
            is_complete = self.are_recent_reviews_complete(provider, True, False)
            if not is_complete :
                successCount -= 1
                print("Expected to find a complete reviews without an author from the provider:" + provider)

        self.assertEqual(successCount, expectedCount, "Expected to find reviews just without an author for : " + ", ".join(expected_without_author))

    def test_ensure_all_reviews_from_today_without_author(self):
        successCount = expectedCount = len(expected_without_author)
        actual_failed_providers = []
        for provider in expected_without_author:
            is_missing = self.recent_reviews_are_missing_field(provider, False, True)
            if not is_missing :
                successCount -= 1
                print("Expected to find all reviews without an author from the provider:" + provider)

        self.assertEqual(successCount, expectedCount, "Expected to find all reviews without an author for : " + ", ".join(actual_failed_providers))

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

    def recent_reviews_are_missing_field(self, provider, has_no_rating=False, has_no_author=False, has_no_date=False, has_no_excerpt=False):

        reviews = Review.select().where(Review.provider == provider).where(Review.created_at > few_hours_ago)
        if has_no_rating:
            reviews = reviews.select().where(~(Review.rating))

        if has_no_author:
            reviews = reviews.select().where(~(Review.author))

        if has_no_date:
            reviews = reviews.select().where(~(Review.date))

        if has_no_excerpt:
            reviews = reviews.select().where(~(Review.excerpt))

        return reviews.count() == 0

if __name__ == '__main__':
    unittest.main()
