## SweetIQ python web application template

Simple python / frontend application to consume the sweetiQ API. Python layer built around flask and peewee, tested with
a SQLite database, MySQL / PostgreSQL should work fine (TODO Test this). The HTML layer is built around jQuery, with
the addition of Semantic UI to give it a clean look. The javascript layer to communicate with the python web app only
has jQuery as a dependency.

### Running the app

- Update the `lib/config.py` file to your requirements, e.g. fill in your sweetiQ API key.
- `pip install -r requirements.txt`
- `python python-api-webapp.py`
- Navigate to http://localhost:5000

## Location auditing
This application was built as a tester for the sweetIQ location auditing API. The API invokes crawling of specific
directories to find profile pages that more than likely contain the provided location's Name, Address and Phone
information. Reviews are also scraped if they are available.

#### API features
An endpoint with the following structure:
GET - https://dd.api.gmlapi.com:8080/presence-api?api_key=YOUR_API_KEY
Fails if these is no api_key set.

Accepts a JSON object of the following format as query params.

```javascript 
{
    "location":{
        "name": "Schwartz's",
        "address": "3895 Boulevard Saint-Laurent",
        "city": "Montreal",
        "province": "Quebec",
        "country": "Canada",
        "postal": "H2W 1L2",
        "phone": "(514) 842-4813"
    },
    "validation_weights":{   
        "name": 1.0,
        "address": 1.0,
        "city": 1.0,
        "province": 0.3,
        "country": 1.0,
        "postal": 0.4,
        "phone": 0.5
    },
    "verified_cutoff": 0.7,
    "listing_callback_url": "http://myEndPoint/to/call/for/all/listings",
    "review_callback_url": "http://myEndPoint/to/call/for/all/reviews",
    "completed_callback_url": "http://myEndPoint/to/call/when/crawling/is/done/"

}
```

Besides hunting for location profiles on the directories of your choice, the API also exposes some properties to help
ascertain the quality of the discovered locations and reduce the number of inaccuracies.

#### validation_weights
- A json object that allows for adjusting the weights assigned to the NAP (name, address, phone) properties when
validating addresses.
- Adjust these for locations that have many phone numbers by setting the "phone" property to 0
- Adjust these for service area businesses that have no physical address by setting the "address" property to 0

#### verified_cutoff
- A float value less than 1 which toggles the status between "verified" and "not me". Suggested value is 0.7 but
making this number higher will provide fewer but more accurate results and some valid listings may have their status
set to "not me"

### Other features
#### daily test run
- Setup a test that runs daily to ensure that you are getting listings from the subscribed to directories. Be sure to
add locations that have profiles on all the directories.


### Recommendations

#### Important

- Set up your own API key in the `lib/config.py` file
- Enable SSL on your webapp (otherwise your api_key in the query string parameters is readable by everyone)
- Connect your app to PostgreSQL / MySQL instead of the default SQLite database

### Development notes

- Make sure your callback address that you configure is accessible from the web, in other words make sure your firewall
is not blocking http requests to your dev setup.
- Database migrations must be done manually, so when changing model definitions, make sure to run the proper SQL
commands to update the database schema.


### Testing

Yep, there's a test suite , make sure the tests are passing when making your changes. (`nosetests test/`)