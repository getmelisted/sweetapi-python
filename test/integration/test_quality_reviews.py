__author__ = 'jasonrudland'

from datetime import datetime, timedelta


from lib.models import Review

import unittest

class MyTestCase(unittest.TestCase):

    global few_hours_ago
    few_hours_ago = datetime.now() - timedelta(hours=6)

    def ensure_recent_reviews_are_complete(self, provider, has_rating=True, has_author=True,has_date=True, has_excerpt=True):

        try:
            reviews = Review.select().where(Review.provider == provider).where(Review.created_at > few_hours_ago)
            if reviews.count() and has_rating:
                reviews = reviews.select().where(Review.rating > 0)

            if reviews.count() and has_author:
                reviews = reviews.select().where(Review.author.regexp(".{3,}"))

            if reviews.count() and has_date:
                reviews = reviews.select().where(Review.date.regexp("\D*\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d"))

            if reviews.count() and has_excerpt:
                reviews = reviews.select().where(Review.excerpt.regexp(".{10,}"))

            return reviews.count() > 0
        except Exception as e:
            print 'Explosion' + e.message

        return False


    def test_recent_reviews_are_complete_for_google(self):
        provider = "google"
        has_complete = self.ensure_recent_reviews_are_complete(provider)
        self.assertTrue(has_complete, "Expected to find a valid review from the provider:" + provider)

    def test_recent_reviews_are_complete_for_facebook(self):
        provider = "facebook"
        has_complete = self.ensure_recent_reviews_are_complete(provider)
        self.assertTrue(has_complete, "Expected to find a valid review from the provider:" + provider)

    def test_recent_reviews_are_complete_for_yahoo(self):
        provider = "yahoo"
        has_complete = self.ensure_recent_reviews_are_complete(provider)
        self.assertTrue(has_complete, "Expected to find a valid review from the provider:" + provider)

    def test_recent_reviews_are_complete_for_bing(self):
        provider = "bing"
        has_complete = self.ensure_recent_reviews_are_complete(provider)
        self.assertTrue(has_complete, "Expected to find a valid review from the provider:" + provider)

    def test_recent_reviews_are_complete_for_yelp(self):
        provider = "yelp"
        has_complete = self.ensure_recent_reviews_are_complete(provider)
        self.assertTrue(has_complete, "Expected to find a valid review from the provider:" + provider)


if __name__ == '__main__':
    unittest.main()
