# ISTE 610 MongoDB Project

This project is a web search application built using Flask and MongoDB that allows users to search data where the [Google Local Data](https://jiachengli1995.github.io/google/index.html) is used as the database which contains review information on Google map (ratings, text, images, etc.), business metadata (address, geographical info, descriptions, category information, price, open hours, and MISC info), and links (relative businesses) up to Sep 2021 in the United States.

The following are the group members:

* Hemant Rattey
* Nikhil Malkari
* Ajay Kumar Venkata Vutty
* Rahul Jaggaiahgari

## Table of Contents

* [Technologies Used](#technologies-used)
* [Data Cleaning and Preprocessing](#Data-Cleaning-and-Preprocessing)
* [Scraping Google Maps for Images](#Scraping-Google-Maps-for-Images)
* [Loading the Database](#Loading-the-Database)
* [Building the Application](#Building-the-Application)
* [Features](#Features)
* [Challenges Faced](#Challenges-Faced)

## Technologies Used

The project uses the following technologies:

- flask: a Python web framework
- pymongo: a Python library for MongoDB
- geopy: a Python library for geocoding and distance calculations
- bson: a Python library for working with BSON (Binary JSON) data
- opencage: a Python library for geocoding using OpenCage Geocoder API
- selenium: a Python library for automating web browsers
- pandas: a Python library for data manipulation and analysis

We mainly used flask because it is a lightweight and flexible web framework, making it an ideal choice for a class project that requires building a web application on small scale. With its modular design and easy setup, Flask allows for quick development and iteration, while its large community and integration with other technologies provide ample resources for troubleshooting and adding new features. Additionally, Flask's built-in testing support can simplify the testing process and ensure the project is functioning as expected.

We also used basic HTML and CSS for the front-end development that added some basic styling to the project. HTML and CSS provide foundations for creating a visually appealing and functional user interface.

## Data Cleaning and Preprocessing

- The original data is too large and contains around 700 million reviews for around 5 million businesses. But, the data is provided state-wise, so we manually selected 7 states namely `Alaska, DC, Hawaii, Maryland, Massachusetts, Minnesota and New Jersey` and worked with the data for these states.
- After getting the data we are working with, we looked at the structure of the data and it was pretty unstructured. It was in JSON format but each document represented a review by a user, which was uniquely identified by `user_id`.
- So, to make the data structured in a way that all details for a business is represented a one document and we aggregated all the reviews for the businesses. Each document is unique and is identified using `business_id`.
- We did all the cleaning and preprocessing in separate Jupyter notebooks for each state and for this processes, we used `pandas`. The scripts output a JSON file. Thus, we got 7 JSON files for the 7 states. In total, we had 200,166 businesses across the 7 states.

## Scraping Google Maps for Images

- Once we had the JSON files, we needed to get the corresponding images for the businesses.
- For this process, we used `selenium` to automate the process of scraping the images. The JSON files generated previously contains a field that stores the google maps link for the business.
- We used these google maps links to scrape about 700 images for 700 businesses. These images were stored locally, hence we scraped a limited number of images.
- To ensure data integrity and that the image belongs to the said business, we stored the images as *`business_id.jpg`* in the local system.

## Loading the Database

- For the preliminary database, we uploaded the 7 JSON files generated for each state. for which we used the `mongoimport` command.
- The next step was to upload the images to the database using GridFS. For this, we wrote a script named `gridfs.ipynb` that traverses through a folder of images and looks at the filename and finds the corresponding business document and then uploads the image using gridfs `put` method and updates the said document to add a field named `image_id` that stores the `_id` of the `fs.files` collection. This makes it easier to retrieve the image later on and ensures data integrity.
- Finally, once we had the images in GridFS, we converted the latitude and longitude fields in the collection to a GeoJSON object to help with geospatial queries.
- Once the database was loaded, we had the following 3 collections and the corresponding count of documents:

> 1. businesses: 200,166 documents
> 2. fs.files: 672 documents
> 3. fs.chunks: 709 documents (since image sizes were small, only 1 chunk per image was created except for the default image).

## Building the Application

- For building the backend of the application, we used Flask and Python.
- In Flask, we defined routes to handle incoming requests and appropriately implemented the backend functionality to work with MongoDB using Pymongo.
- Using flask, you can render templates and get HTML webpages which we customized using some basic HTML and CSS stylings.
- We then used geopy and OpenCage API to handle the geocoding and geospatial queries.

## Features

The application currently has the following features:

- ***Search by business name***: The user can enter a partial string that can search for business name and the application returns a list of documents that match the query from the user. In the backend, we performed a regex find query using word boundaries.
- ***Search by location***: The user has the ability to enter latitude and longitude along with the maximum distance that searches for businesses in the provided proximity to a given point in a two-dimensional space by the user. The user can also put a rating which searches for businesses having average rating above the one provided by the user.
- ***Search by address***: The user also has the ability to search by street address and use the prompts for maximum distance as well as ratings.

## Challenges Faced

1. First and foremost, we faced problems with cleaning and structuring the data in the format we wanted. Since the files were quite big, we worked on smaller samples of data to build scripts then ran them on the data for the 7 states.
1. Next, one of the most challenging parts was to scrape the Google Maps website for the images. We explored the usage of Google APIs but they were paid.So, we ended up making a web scraper using `selenium` which is an open-source tool used for automating web browsers.
1. Finally, we had to learn how to use `opencage` and `geopy` for handling the conversion from street address to latitude, longitude. Other alternatives were using Google Maps Geocoding API and Mapbox Geocoding API, but they were paid and provided very less requests per day.

## Running the Application

- When you clone the github repo, it creates a folder named `mongo-project-aamudach`. Go into this folder and create a new virtual environment using conda, pipenv or venv. Then, add the dependencies and packages using the command `pip install -r requirements.txt`.
- Once the dependencies are installed, you can run the application using the command `python app.py`. This runs a flask instance in the terminal and you can visit `http://127.0.0.1:5000/` in any browser and use the application there.
