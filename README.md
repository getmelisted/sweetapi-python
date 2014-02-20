## sweetiQ python web application template

Simple python / frontend application to consume the sweetiQ API. Python layer built around flask and peewee, tested with
a SQLite database, MySQL / PostgreSQL should work fine (TODO Test this). The HTML layer is built around jQuery, with
the addition of Semantic UI to give it a clean look. The javascript layer to communicate with the python web app only
has jQuery as a dependency.

### Running the app

- Update the `lib/config.py` file to your requirements, e.g. fill in your sweetiQ API key.
- `pip install -r requirements.txt`
- `python python-api-webapp.py`
- Navigate to http://localhost:5000


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