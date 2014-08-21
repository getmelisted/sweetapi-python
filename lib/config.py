__author__ = 'pat'

debug = True

local_api_key = 'YOUR_API_KEY__CHANGE_ME'

sweetiq_api_url = 'https://api.sweetiq.com:8080/'
sweetiq_api_key = 'YOUR_SWEETIQ_API_KEY'
sweetiq_api_listing_callback_url = 'http://localhost:5000/api/location/listing?api_key=%s' % local_api_key
sweetiq_api_review_callback_url = 'http://localhost:5000/api/location/review?api_key=%s' % local_api_key
sweetiq_api_completed_callback_url = 'http://localhost:5000/api/location/completed?api_key=%s' % local_api_key

