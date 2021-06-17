import gmplot 
import os

API_KEY = os.environ.get('MAPS_API_KEY')

#plot center of map and zoom level
gmap = gmplot.GoogleMapPlotter(47.608013,-122.335167, 10, apikey=API_KEY)

#plot coordinates
gmap.coloricon = "http://www.googlemapsmarkers.com/v1/%s/"
gmap.marker(48.1013714, -122.2271894, "blue", marker=False)

#draw circle around marker, radius in meters
#200 feet = 60.96 meters
gmap.circle(48.1013714, -122.2271894, 60.96)

#where to draw map (. = current directory)
gmap.draw(".\map.html")