# Surfs Up!

## Step 1 - Climate Analysis and Exploration

The file "climate_starter.ipynb" shows analysis and exploration of weather station data contained in the hawaii.sqlite database. The general intent was to view precipitation and temperature ranges for specific dates in order to prepare for a trip to Hawaii.

- - -

## Step 2 - Climate App

The file "app.py" is a Flask API based on the queries developed in the climate starter notebook. Various routes were created to return data in JSON format. Since certain routes rely on certain date formatting in the URL string, an effort was made to error check input.