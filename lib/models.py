import datetime
import json

__author__ = 'pat'

from peewee import *

database = SqliteDatabase('location_data.db')
database.connect()


import logging
logger = logging.getLogger('peewee')
logger.setLevel(logging.WARN)

class BaseModel(Model):
    class Meta:
        database = database

    def to_dict(self):
        result = {}
        for key in self._data:
            value = self._data[key]
            if isinstance(value, datetime.datetime):
                result[key] = str(value)
            else:
                result[key] = value
        return result

    def to_json(self):
        return json.dumps(self.to_dict())


class Location(BaseModel):
    id = PrimaryKeyField(primary_key=True, null=False)
    token_id = CharField()
    name = CharField()
    address = CharField()
    city = CharField(null=True)
    province = CharField(null=True)
    country = CharField(null=True)
    postal = CharField(null=True)
    phone = CharField(null=True)

    is_completed = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    completed_at = DateTimeField(default=None, null=True)

    class Meta:
        indexes = (
            # create a unique index on token_id
            (('token_id'), True)
        )

    def location_stats(self):
        return {
            'total_listings': self.listings.count(),
            'verified_listings': self.listings.where(Listing.status == 'verified').count(),
            'not_me_listings': self.listings.where(Listing.status == 'not_me').count(),
            'pending_listings': self.listings.where(Listing.status == 'pending').count(),
            'duplicate_listings': self.listings.where(Listing.status == 'duplicate').count(),
            'total_reviews': self.reviews.count(),
            'verified_reviews': self.listings.where(Listing.status == 'verified').join(Review).count(),
            'reviews_requiring_attention': self.listings.
                where(Listing.status == 'verified').
                join(Review).where(Review.rating < 3).count()
        }

    @staticmethod
    def create_location(token_id, location_data):
        location = Location(token_id=token_id,
                            name=location_data.get('name'),
                            address=location_data.get('address'),
                            city=location_data.get('city'),
                            province=location_data.get('province'),
                            country=location_data.get('country'),
                            postal=location_data.get('postal'),
                            phone=location_data.get('phone'))

        location.save(force_insert=True)

        return location

    @staticmethod
    def location_completed(token_id):
        location = Location.get(Location.token_id == token_id)
        location.is_completed = True
        location.completed_at = datetime.datetime.now()
        location.save()


class Listing(BaseModel):
    id = PrimaryKeyField(primary_key=True, null=False)
    location = ForeignKeyField(Location, related_name='listings', null=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    name = CharField(null=True)
    status = CharField(null=True)
    unique_hash = CharField()
    provider = CharField(null=True)
    domain = CharField(null=True)
    accuracy = FloatField(null=False,default=0)
    link = CharField(null=True)
    address = CharField(null=True)
    phone = CharField(null=True)

    class Meta:
        indexes = (
            (('unique_hash'), False),
            (('location_id'), False)
        )

    @staticmethod
    def save_listing(location, unique_hash, listing_data):

        accuracy = float(str(listing_data.get('accuracy','0.0'))[:4])
        try:


            listing = Listing.get(Listing.location == location, Listing.unique_hash == unique_hash)

            # Unique hash shouldn't be updated
            listing.name = listing_data.get('name')
            listing.status = listing_data.get('status')
            listing.provider = listing_data.get('provider')
            listing.domain = listing_data.get('domain')
            listing.accuracy = accuracy
            listing.link = listing_data.get('link')
            listing.address = listing_data.get('address')
            listing.phone = listing_data.get('phone')

            listing.save()

        except DoesNotExist:
            listing = Listing(location=location,
                              unique_hash=unique_hash,
                              name=listing_data.get('name'),
                              status=listing_data.get('status'),
                              provider=listing_data.get('provider'),
                              domain=listing_data.get('domain'),
                              accuracy=accuracy,
                              link=listing_data.get('link'),
                              address=listing_data.get('address'),
                              phone=listing_data.get('phone'))

            listing.save()

        return listing


class Review(BaseModel):
    id = PrimaryKeyField(primary_key=True, null=False)
    location = ForeignKeyField(Location, related_name='reviews', null=False, )
    listing = ForeignKeyField(Listing, related_name='reviews', null=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    unique_hash = CharField()
    review_id = CharField()
    provider = CharField()
    date = DateTimeField(null=True)
    author = CharField(null=True)
    author_id = CharField(null=True)
    rating = FloatField(null=False,default=0)
    link = CharField(null=True)
    excerpt = CharField(null=True)

    class Meta:
        indexes = (
            (('location_id'), False),
            (('listing_id'), False)
        )

    @staticmethod
    def save_review(location, listing, review_data):

        if not listing:
            # Stub out a listing since we haven't received its information yet
            listing = Listing.save_listing(location, review_data['unique_hash'], {'address':'For reviews without associated listing!'})

        try:

            review = Review.get(Review.listing == listing, Review.review_id == review_data.get('review_id'))

            # Review id shouldn't be updated
            review.unique_hash = review_data.get('unique_hash')
            review.date = review_data.get('date')
            review.provider = review_data.get('provider')
            review.author = review_data.get('author')
            review.author_id = review_data.get('author_id')
            review.rating = review_data.get('rating')
            review.link = review_data.get('link')
            review.excerpt = review_data.get('excerpt')

            review.save()

        except DoesNotExist:
            review = Review(location=location,
                            listing=listing,
                            unique_hash=review_data.get('unique_hash'),
                            review_id=review_data.get('review_id'),
                            date=review_data.get('date'),
                            provider=review_data.get('provider'),
                            author=review_data.get('author'),
                            author_id=review_data.get('author_id'),
                            rating=review_data.get('rating'),
                            link=review_data.get('link'),
                            excerpt=review_data.get('excerpt'))

            review.save()

        return review


# Initialization code for the tables
try:
    Location.create_table()
except:
    pass

try:
    Listing.create_table()
except:
    pass

try:
    Review.create_table()
except:
    pass