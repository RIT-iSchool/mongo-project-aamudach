from pymongo.errors import PyMongoError
from flask import Flask, render_template, request, redirect, url_for, abort
import pymongo
from geopy.distance import geodesic
from bson.son import SON
from geopy.geocoders import GoogleV3
from opencage.geocoder import OpenCageGeocode
from urllib.parse import quote
from gridfs import GridFS
from bson import ObjectId
import base64

app = Flask(__name__)


try:
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client['project']
    collection = db['businesses']
    fs_files = db['fs.files']
    fs_chunks = db['fs.chunks']
    grid_fs = GridFS(db)
    collection.create_index([('location', pymongo.GEOSPHERE)])
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
        
        search_results = []

        if results:
            for result in results:

                lat = result['location']['coordinates'][1]
                lng = result['location']['coordinates'][0]
                address = result['address']
                avg_rating = result['avg_rating']
                business_id = result['business_id']
                #image_url = result['image_url']

                search_results.append({'business_name': result['business_name'], 'latitude': lat, 'longitude': lng,
                                      'address': address, 'avg_rating': avg_rating, 'business_id': result['business_id']})
                
                if len(search_results) == 0:
                    message = "No Businesses found. Please try again with different search address/criteria."
                    return render_template('search_results_l.html', message=message)
                    
        return render_template('search_results_l.html', results=search_results)
    return render_template('search_location.html')


app.config['OPENCAGE_API_KEY'] = '53e5502771ec4437aab8f4f3f7b86096'


@app.route('/search_by_address', methods=['GET', 'POST'])
def search_by_address():
    if request.method == 'POST':

        address = request.form['address']
        distance = request.form['distance']
        avg_rating = request.form['avg_rating']

        geocoder = OpenCageGeocode(app.config['OPENCAGE_API_KEY'])
        results = geocoder.geocode(address)

        if results:
            latitude = results[0]['geometry']['lat']
            longitude = results[0]['geometry']['lng']

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

            search_results = []
            for result in results:

                lat = result['location']['coordinates'][1]
                lng = result['location']['coordinates'][0]
                address = result['address']
                avg_rating = result['avg_rating']
                business_id = result['business_id']
                #image_url = result['image_url']

                search_results.append({'business_name': result['business_name'], 'latitude': lat, 'longitude': lng,
                                      'address': address, 'avg_rating': avg_rating, 'business_id': result['business_id']})
                
            if len(search_results) == 0:
                message = "No Businesses found. Please try again with different search address/criteria."
                return render_template('search_results_a.html', message=message)

            return render_template('search_results_a.html', results=search_results)

    return render_template('search_by_address.html')


@app.route('/search_business', methods=['GET', 'POST'])
def search_business():
    if request.method == 'POST':
        business_name = request.form['business-name']

        results = collection.find(
            {"business_name": {"$regex": f"\\b{business_name}\\w*\\b", "$options": "i"}})
        
        search_results = []
        for result in results:

            lat = result['location']['coordinates'][1]
            lng = result['location']['coordinates'][0]
            address = result['address']
            #image_url = result['image_url']

            search_results.append({'business_name': result['business_name'], 'latitude': lat,
                                  'longitude': lng, 'address': address, 'business_id': result['business_id']})
            
        if len(search_results) == 0:
            message = "No businesses found. Please try again with different business name."
            return render_template('search_results_b.html', message=message)

        return render_template('search_results_b.html', results=search_results)
    return render_template('search_business.html')


@app.route('/business/<business_id>')
def business_page(business_id):
    # Query the database for the business document with the matching business_id
    business = collection.find_one({'business_id': business_id})
    if business:
        # Render the business page template with the business data
        if 'image_id' in business:
            try:
                image_id = ObjectId(business['image_id'])
                image_file = grid_fs.get(image_id).read()
                image_base64 = base64.b64encode(image_file).decode('utf-8')
            except:
                # Handle the case where the image is not found
                image_base64 = None
        else:
            image_base64 = None
        comments = business.get('comments', [])

        return render_template('business.html', business=business, image_base64=image_base64, comments=comments)
    else:
        # If the business isn't found, return a 404 error
        abort(404)


@app.route('/business/<business_id>/submit_comment', methods=['POST'])
def submit_comment(business_id):
    # Get form data
    user_name = request.form['user_name']
    comment_text = request.form['comment_text']

    # Create a comment document
    comment = {
        'user_name': user_name,
        'comment_text': comment_text
    }

    # Add the comment to the business' comments array
    collection.update_one({'business_id': business_id}, {
                          '$push': {'comments': comment}})

    # Redirect back to the business page
    return redirect(url_for('business_page', business_id=business_id))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
