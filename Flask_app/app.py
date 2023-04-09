from flask import Flask, render_template, request, redirect, url_for
from flask import Flask, render_template, request, redirect, url_for
import pymongo
from geopy.distance import geodesic
from bson.son import SON
from geopy.geocoders import GoogleV3
from geopy.distance import geodesic
from opencage.geocoder import OpenCageGeocode
from flask import Flask, render_template, abort
from flask import Flask, render_template, url_for
from urllib.parse import quote


app = Flask(__name__)

from pymongo.errors import PyMongoError

try:
    client = pymongo.MongoClient("mongodb://user:student@127.0.0.1:27017/project")
    db = client['project']
    collection = db['businesses']
except PyMongoError as e:
    print(f"Error connecting to MongoDB: {e}")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_location', methods=['GET', 'POST'])
def search_location():
    if request.method == 'POST':
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        distance = request.form['distance']
        avg_rating = request.form['avg_rating']


        latitude = float(latitude)
        longitude = float(longitude)
        distance = float(distance)
        avg_rating = float(avg_rating)

        
        results = collection.find({
            'location': {
                '$near': {
                    '$geometry': {
                        'type':"Point",
                        'coordinates':[longitude, latitude]
                    },
                    '$maxDistance': distance
                }
            },
            'avg_rating': {
                '$gte': avg_rating
            }
        })

        return render_template('search_results.html', results=results)
    return render_template('search_location.html')


app.config['OPENCAGE_API_KEY'] = '2075d13a74c74ce6966b09b239d52c8d'

@app.route('/search_by_address', methods=['GET', 'POST'])
def search_by_address():
    if request.method == 'POST':
        
        address = request.form['address']
        distance = request.form['distance']

        
        geocoder = OpenCageGeocode(app.config['OPENCAGE_API_KEY'])
        results = geocoder.geocode(address)

        
        if results:
            latitude = results[0]['geometry']['lat']
            longitude = results[0]['geometry']['lng']

            
            distance = float(distance)

            
            results = collection.find({
                'location': {
                    '$near': {
                        '$geometry': {
                            'type': "Point",
                            'coordinates': [longitude, latitude]
                        },
                        '$maxDistance': distance
                    }
                }
            })

            
            search_results = []
            for result in results:
                
                lat = result['location']['coordinates'][1]
                lng = result['location']['coordinates'][0]
                address = result['address']
                #image_url = result['image_url']

                
                search_results.append({'business_name': result['business_name'], 'latitude': lat, 'longitude': lng, 'address': address})

            return render_template('search_results.html', results=search_results)
        else:
            
            return render_template('search_by_address.html', error='Location not found')

    return render_template('search_by_address.html')

@app.route('/search_business', methods=['GET', 'POST'])
def search_business():
    if request.method == 'POST':
        business_name = request.form['business-name']

        
        results = collection.find({"business_name": {"$regex": business_name, "$options": "i"}})

        
        search_results = []
        for result in results:
           
            lat = result['location']['coordinates'][1]
            lng = result['location']['coordinates'][0]
            address = result['address']
            #image_url = result['image_url']

            
            search_results.append({'business_name': result['business_name'], 'latitude': lat, 'longitude': lng, 'address': address})

        return render_template('search_results.html', results=search_results)
    return render_template('search_business.html')

@app.route('/business/<business_name>')
def business_page(business_name):
    # Query the database for the business document with the matching business_name
    my_string = business_name
    business_name = my_string.replace("%20", " ")
    business = collection.find_one({'business_name': business_name})

    if business:
        # Render the business page template with the business data
        return render_template('business.html', business=business)
    else:
        # If the business isn't found, return a 404 error
        abort(404)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
