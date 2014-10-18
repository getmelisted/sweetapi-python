import json

import flask
from flask import Flask, render_template
from peewee import DoesNotExist
import requests

from lib import config
from lib.http_auth import requires_auth
from lib.models import Location, Listing, Review
from lib.sweetiq_api import SweetiqAPI


app = Flask(__name__)

sweetiqApi = SweetiqAPI(requests)


@app.route('/')
@requires_auth
def index():
    return render_template('index.html')


@app.route('/location', methods=['POST'])
@requires_auth
def run_location():
    location_data = {}
    for key in ['name', 'address', 'city', 'province', 'country', 'postal', 'phone']:
        location_data[key] = flask.request.form[key]

    result = sweetiqApi.run_location(location_data, flask.request.form["account_api_key"])

    if 'success' not in result or not result['success']:
        app.logger.error('Failed to trigger run location request to sweetiQ API', result)
        return flask.Response(status=500)
    else:
        token_id = result['token_id']
        location = Location.create_location(token_id, location_data)
        return flask.json.dumps(location.to_dict())


@app.route('/api/location/listing', methods=['PUT', 'POST'])
@requires_auth
def accept_listing():
    app.logger.debug('Received listing')

    listing = json.loads(flask.request.form['listing'])
    unique_hash = flask.request.form['unique_hash']
    listing['unique_hash'] = unique_hash
    token_id = flask.request.form['token_id']

    try:
        location = Location.get(Location.token_id == token_id)
        listing = Listing.save_listing(location, unique_hash, listing)

        return flask.Response(status=204)
    except DoesNotExist:
        return flask.Response(status=404)


@app.route('/api/location/review', methods=['PUT', 'POST'])
@requires_auth
def accept_review():
    app.logger.debug('Received review')

    unique_hash = flask.request.form['unique_hash']
    token_id = flask.request.form['token_id']
    review = json.loads(flask.request.form['review'])
    review['provider'] = flask.request.form['provider']
    review['unique_hash'] = unique_hash

    try:
        location = Location.get(Location.token_id == token_id)
        listing = None

        try:
            listing = Listing.get(Listing.location == location, Listing.unique_hash == unique_hash)
        except DoesNotExist:
            # save_review will stub out a listing
            pass

        review = Review.save_review(location, listing, review)
        return flask.Response(status=204)
    except DoesNotExist:
        return flask.Response(status=404)


@app.route('/api/location/completed', methods=['PUT', 'POST'])
@requires_auth
def accept_completed():
    app.logger.debug('Received completed')

    token_id = flask.request.form['token_id']

    Location.location_completed(token_id)

    return flask.Response(status=204)


@app.route('/locations', methods=['GET'])
@requires_auth
def get_locations():
    locations = Location.select()

    json = []
    for location in locations:
        json.append(location.to_dict())

    return flask.json.dumps(json)


@app.route('/location/<id>', methods=['GET'])
@requires_auth
def get_location(id):
    try:
        location = Location.get(Location.id == id)
        stats = location.location_stats()

        return flask.json.dumps(dict(location.to_dict().items() + stats.items()))
    except DoesNotExist:
        return flask.Response(status=404)

@app.route('/location/<id>', methods=['DELETE'])
@requires_auth
def delete_location(id):
    try:
        location = Location.get(Location.id == id)
        location.delete_instance(recursive=True)
        return flask.Response(status=204)
    except DoesNotExist:
        return flask.Response(status=404)


@app.route('/location/<id>/reviews', methods=['GET'])
@requires_auth
def get_location_reviews(id):
    try:
        location = Location.get(Location.id == id)
        reviews = location.reviews
        json = []
        for review in reviews:
            json.append(review.to_dict())

        return flask.json.dumps(json)
    except DoesNotExist:
        return flask.Response(status=404)

@app.route('/location/<id>/listings', methods=['GET'])
@requires_auth
def get_location_listings(id):
    try:
        location = Location.get(Location.id == id)
        listings = location.listings
        json = []
        for listing in listings:
            json.append(listing.to_dict())

        return flask.json.dumps(json)
    except DoesNotExist:
        return flask.Response(status=404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=config.debug, use_reloader=False, port=5000)
