from cloudant.client import Cloudant
from cloudant.query import Query
from flask import Flask, jsonify, request
import atexit
import json

# TODO: Enter Your Creditentials
#Add your Cloudant service credentials here
cloudant_username = 'ENTER_YOUR_CLOUDANT_USERNAME'
cloudant_api_key = 'ENTER_YOUR_IAM_API_KEY'
cloudant_url = 'ENTER_YOUR_CLOUDANT_URL'
client = Cloudant.iam(cloudant_username, cloudant_api_key, connect=True, url=cloudant_url)

session = client.session()
print('Databases:', client.all_dbs())

db = client['reviews']

app = Flask(__name__)

@app.route('/api/get_reviews', methods=['GET'])
def get_reviews():
    dealership_id = request.args.get('id')

    # Check if "id" parameter is missing
    if dealership_id is None:
        return jsonify({"error": "Missing 'id' parameter in the URL"}), 400

    # Convert the "id" parameter to an integer (assuming "id" should be an integer)
    try:
        dealership_id = int(dealership_id)
    except ValueError:
        return jsonify({"error": "'id' parameter must be an integer"}), 400

    # Define the query based on the 'dealership' ID
    selector = {
        'dealership': dealership_id
    }

    # Execute the query using the query method
    result = db.get_query_result(selector)

    # Create a list to store the documents
    data_list = []

    # Iterate through the results and add documents to the list
    for doc in result:
        data_list.append(doc)

    # Return the data as JSON
    return jsonify(data_list)


@app.route('/api/post_review', methods=['POST'])
def post_review():
    if not request.json:
        abort(400, description='Invalid JSON data')
    
    # Extract review data from the request JSON
    review_data = request.json

    # Validate that the required fields are present in the review data
    required_fields = ['id', 'name', 'dealership', 'review', 'purchase', 'purchase_date', 'car_make', 'car_model', 'car_year']
    for field in required_fields:
        if field not in review_data:
            jsonify(400, {"description":f'Missing required field: {field}'})

    # Save the review data as a new document in the Cloudant database
    # Temprory solution for case: If direct submission of reveiw from flask server.
    print(review_data)
    temp = {}
    if(type(review_data) == type(temp)):
        db.create_document(review_data)
        return jsonify({"message": "Review posted successfully"}), 201
        
        
    # Review submission via post request from django server
    print(review_data["review"])
    db.create_document(review_data["review"])
    return jsonify({"message": "Review posted successfully"}), 201

if __name__ == '__main__':
    app.run(debug=True)