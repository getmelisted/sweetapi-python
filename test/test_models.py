import random

from peewee import SelectQuery

from lib import models
from lib.models import Location, Listing, Review


__author__ = 'pat'

import unittest


class MyTestCase(unittest.TestCase):
    def _create_location(self):
        initial_count = SelectQuery(Location).count()

        location = models.Location.create_location(random.randint(1, 1000000), {
            'name': 'Schwartz\'s',
            'address': '3895 Boulevard Saint-Laurent',
            'city': 'Montreal',
            'province': 'Quebec',
            'country': 'Canada',
            'postal': 'H2W 1L2',
            'phone': '(514) 842-4813'
        })

        self.assertEqual(initial_count + 1, SelectQuery(Location).count())
        return location

    def _delete_location(self, location):
        location.delete_instance(recursive=True)

    def _create_listing(self, location, listing_data = {}):
        initial_count = SelectQuery(Listing).count()

        unique_hash = random.randint(1, 100000)

        default_listing_data = {'name': 'Test listing',
                                'domain': 'google.ca',
                                'provider': 'google',
                                'status': 'verified',
                                'link': 'http://plus.google.com/schwartzs',
                                'address': '3895 Saint Laurent boulevard',
                                'phone': '(514) 842-4813',
                                'accuracy': 0.93,
                                'excerpt': None
        }

        for key in default_listing_data:
            if key not in listing_data:
                listing_data[key] = default_listing_data[key]

        listing = models.Listing.save_listing(location, unique_hash, listing_data)

        self.assertEqual(initial_count + 1, SelectQuery(Listing).count())
        return listing

    def _delete_listing(self, listing):
        listing.delete_instance(recursive=True)

    def _create_review(self, location, listing, review_data={}):
        initial_count = SelectQuery(Review).count()

        review_id = random.randint(1, 100000)

        default_review_data = {'review_id': review_id,
                               'unique_hash': 'hash-%s' % review_id,
                               'date': '2009-10-17T17:57:43',
                               'provider': 'google',
                               'author': 'Joe Patate',
                               'author_id': '123112312311',
                               'rating': 1,
                               'link': 'http://plus.google.com/1978498172409874/about',
                               'excerpt': 'Pizza is awesome.'}

        for key in default_review_data:
            if key not in review_data:
                review_data[key] = default_review_data[key]

        review = models.Review.save_review(location, listing, review_data)

        self.assertEqual(initial_count + 1, SelectQuery(Review).count())
        return review

    def _delete_review(self, review):
        review.delete_instance(recursive=True)

    def test_can_create_location(self):
        location = self._create_location()

        self.assertIsNotNone(location.name)
        self.assertIsNotNone(location.address)
        self.assertIsNotNone(location.city)
        self.assertIsNotNone(location.province)
        self.assertIsNotNone(location.country)
        self.assertIsNotNone(location.postal)
        self.assertIsNotNone(location.phone)

        self._delete_location(location)


    def test_can_complete_location(self):
        location = self._create_location()

        self.assertIsNone(location.completed_at)
        self.assertFalse(location.is_completed)

        Location.location_completed(location.token_id)

        location = Location.get(Location.id == location.id)

        self.assertIsNotNone(location.completed_at)
        self.assertTrue(location.is_completed)

        self._delete_location(location)


    def test_can_create_listing(self):
        location = self._create_location()
        listing = self._create_listing(location)

        self.assertIsNotNone(listing)

        self.assertIsNotNone(listing.name)

        self._delete_listing(listing)
        self._delete_location(location)


    def test_can_update_listing_if_already_exists(self):
        # This is to test the upsert capabilities

        location = self._create_location()
        listing = self._create_listing(location)

        initial_count = SelectQuery(Listing).count()

        # Attempt to 'upsert' the same listing
        Listing.save_listing(location, listing.unique_hash, {
            'name': 'Test2',
            'domain': 'google.ca',
            'provider': 'google',
            'status': 'verified',
            'link': 'http://plus.google.com/schwartzs',
            'address': '3895 Saint Laurent boulevard',
            'phone': '(514) 842-4813',
            'accuracy': 0.93,
            'excerpt': None
        })

        self.assertEqual(initial_count, SelectQuery(Listing).count())

        # Load the listing and make sure its name has been updated
        listing = Listing.get(Listing.id == listing.id)

        self.assertEqual('Test2', listing.name)

        self._delete_listing(listing)
        self._delete_location(location)


    def test_can_create_review(self):
        location = self._create_location()
        listing = self._create_listing(location)
        review = self._create_review(location, listing)

        self.assertEqual(listing, review.listing)
        self.assertEqual(location, review.location)

        self.assertEqual(1, location.reviews.count())
        self.assertEqual(1, listing.reviews.count())

        self._delete_review(review)
        self._delete_listing(listing)
        self._delete_location(location)

    def test_creating_review_without_listing_will_stub_listing(self):
        location = self._create_location()

        initial_listing_count = SelectQuery(Listing).count()
        initial_review_count = SelectQuery(Review).count()

        review = self._create_review(location, None)
        listing = review.listing

        self.assertIsNotNone(listing)
        self.assertEqual(review.unique_hash, listing.unique_hash)

        self.assertEqual(initial_listing_count + 1, SelectQuery(Listing).count())
        self.assertEqual(initial_review_count + 1, SelectQuery(Review).count())

        self._delete_review(review)
        self._delete_listing(review.listing)
        self._delete_location(location)


    def test_can_have_null_rating(self):
        location = self._create_location()
        listing = self._create_listing(location)
        review = self._create_review(location, listing, {
            'rating': None
        })

        self._delete_review(review)
        self._delete_listing(listing)
        self._delete_location(location)


    def test_can_update_review_if_already_exists(self):

        location = self._create_location()
        listing = self._create_listing(location)
        review = self._create_review(location, listing)

        initial_count = SelectQuery(Review).count()

        Review.save_review(location, listing, {
            'review_id': review.review_id,
            'unique_hash': review.unique_hash,
            'date': '2009-10-17T17:57:43',
            'provider': 'new_provider',
            'author': 'Joe Patate',
            'author_id': '123112312311',
            'rating': 5,
            'link': 'http://plus.google.com/1978498172409874/about',
            'excerpt': 'Pizza is awesome.'})

        self.assertEqual(initial_count, SelectQuery(Review).count())

        review = Review.get(Review.location == location, Review.listing == listing,
                            Review.review_id == review.review_id)
        self.assertEqual(5, review.rating)
        self.assertEqual('new_provider', review.provider)

        self._delete_review(review)
        self._delete_listing(listing)
        self._delete_location(location)


    def test_can_delete_location_and_related_elements(self):

        location = self._create_location()
        listing = self._create_listing(location)
        listing2 = self._create_listing(location)

        review = self._create_review(location, listing)
        review2 = self._create_review(location, listing2)

        location_count = SelectQuery(Location).count()
        listing_count = SelectQuery(Listing).count()
        review_count = SelectQuery(Review).count()

        location.delete_instance(recursive=True)

        self.assertEqual(location_count - 1, SelectQuery(Location).count())
        self.assertEqual(listing_count - 2, SelectQuery(Listing).count())
        self.assertEqual(review_count - 2, SelectQuery(Review).count())

    def test_can_serialize_location_to_json(self):

        location = self._create_location()
        self.assertIsNotNone(location.to_json())

        self._delete_location(location)

    def test_can_serialize_listing_to_json(self):

        location = self._create_location()
        listing = self._create_listing(location)

        self.assertIsNotNone(listing.to_json())

        self._delete_listing(listing)
        self._delete_location(location)

    def test_can_serialize_review_to_json(self):

        location = self._create_location()
        listing = self._create_listing(location)
        review = self._create_review(location, listing)

        self.assertIsNotNone(review.to_json())

        self._delete_review(review)
        self._delete_listing(listing)
        self._delete_location(location)

    def test_can_retrieve_location_stats(self):

        location = self._create_location()

        stats = location.location_stats()
        self.assertIsNotNone(stats)
        self.assertEqual(stats['total_listings'], 0)
        self.assertEqual(stats['verified_listings'], 0)
        self.assertEqual(stats['not_me_listings'], 0)
        self.assertEqual(stats['pending_listings'], 0)
        self.assertEqual(stats['duplicate_listings'], 0)
        self.assertEqual(stats['total_reviews'], 0)
        self.assertEqual(stats['verified_reviews'], 0)
        self.assertEqual(stats['reviews_requiring_attention'], 0)

        self._delete_location(location)

    def test_location_stats(self):

        location = self._create_location()

        pending_listing = self._create_listing(location, {'status': 'pending'})
        self._create_listing(location, {'status': 'pending'})
        self._create_listing(location, {'status': 'pending'})
        verified_listing = self._create_listing(location, {'status': 'verified'})
        self._create_listing(location, {'status': 'verified'})
        not_me_listing = self._create_listing(location, {'status': 'not_me'})
        self._create_listing(location, {'status': 'duplicate'})

        self._create_review(location, verified_listing, {'rating': 5})
        self._create_review(location, verified_listing, {'rating': 1})
        self._create_review(location, not_me_listing, {'rating': 5})

        stats = location.location_stats()
        self.assertIsNotNone(stats)
        self.assertEqual(stats['total_listings'], 7)
        self.assertEqual(stats['verified_listings'], 2)
        self.assertEqual(stats['not_me_listings'], 1)
        self.assertEqual(stats['pending_listings'], 3)
        self.assertEqual(stats['duplicate_listings'], 1)
        self.assertEqual(stats['total_reviews'], 3)
        self.assertEqual(stats['verified_reviews'], 2)
        self.assertEqual(stats['reviews_requiring_attention'], 1)

        self._delete_location(location)


if __name__ == '__main__':
    unittest.main()
