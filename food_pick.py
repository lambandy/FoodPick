import tkinter as tk
from tkinter import ttk
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderQuotaExceeded
import requests
import random

class FoodPickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Food Picker")

        # Center the window on the screen
        window_width = 600
        window_height = 400
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Style configuration
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 12))
        style.configure("TButton", background="#4caf50", foreground="black", font=("Arial", 12), padding=(5, 5))

        # Food Type Label and Entry
        food_type_label = ttk.Label(root, text="Enter Food Type:")
        food_type_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.food_type_entry = ttk.Entry(root)
        self.food_type_entry.grid(row=0, column=1, padx=10, pady=10)

        # Location Label and Entry for City Name
        location_label = ttk.Label(root, text="Enter City Name:")
        location_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        self.location_entry = ttk.Entry(root)
        self.location_entry.grid(row=1, column=1, padx=10, pady=10)

        # Distance Label and Entry
        distance_label = ttk.Label(root, text="Enter Distance (miles):")
        distance_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        self.distance_entry = ttk.Entry(root)
        self.distance_entry.grid(row=2, column=1, padx=10, pady=10)

        # Result Label
        self.result_label = ttk.Label(root, text="", style="TLabel")
        self.result_label.grid(row=3, column=0, columnspan=2, pady=20)

        # Button to Trigger Food Selection
        pick_button = ttk.Button(root, text="Pick Food", command=self.pick_food, style="TButton")
        pick_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Button to Choose Random Restaurant
        choose_random_button = ttk.Button(root, text="Choose Random Restaurant", command=self.choose_random_restaurant, style="TButton")
        choose_random_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Variable to store the list of restaurants
        self.restaurants_data = []

    def pick_food(self):
        entered_food_type = self.food_type_entry.get()
        entered_location = self.location_entry.get()
        entered_distance = self.distance_entry.get()

        if entered_food_type and entered_location and entered_distance:
            try:
                # Geocode the entered location to get latitude and longitude
                geolocator = Nominatim(user_agent="food_picker_app")
                location = geolocator.geocode(entered_location, timeout=10)

                if location:
                    latitude, longitude = location.latitude, location.longitude
                else:
                    self.result_label.config(text=f"Location not found: {entered_location}")
                    return

            except (AttributeError, GeocoderTimedOut, GeocoderQuotaExceeded) as e:
                self.result_label.config(text=f"Error geocoding location: {e}")
                return

            try:
                # Convert entered distance to float
                distance = float(entered_distance)
            except ValueError:
                self.result_label.config(text="Please enter a valid distance (numeric value).")
                return

            # Use Yelp API to get restaurant suggestions
            self.restaurants_data = self.get_restaurant_suggestions(entered_food_type, (latitude, longitude), distance)
            result_text = f"Recommended food type: {entered_food_type}\nLocation: {latitude}, {longitude}\nDistance: {distance} miles\n"

            if self.restaurants_data:
                result_text += "\nOpen Restaurants:\n"
                for restaurant in self.restaurants_data:
                    result_text += f"{restaurant['name']} - Rating: {restaurant['rating']}\n"
            else:
                result_text += "No open restaurants found. Try expanding your search criteria."

            self.result_label.config(text=result_text)
        else:
            self.result_label.config(text="Please enter food type, location, and distance.")

    def get_restaurant_suggestions(self, food_type, location, distance):
        # Use Yelp API to get restaurant suggestions
        # Replace 'YOUR_YELP_API_KEY' with your actual Yelp API key
        yelp_api_key = 'hqIKvlHfYSnAgZlrBVWodA3I5m2oMJzYh4OPvD2zsIwWWRoBqwfTLsbreFbqMUOkmwNnT3UzTF-r_5wqIXuyl2D5NOCNfTLAraSzH05WtLW4yAz8MyhGzTuV1WCoZXYx'
        if yelp_api_key == 'YOUR_YELP_API_KEY':
            return []

        headers = {
            'Authorization': f'Bearer {yelp_api_key}',
        }

        params = {
            'term': food_type,
            'latitude': location[0],
            'longitude': location[1],
            'radius': int(distance * 1609.34),  # Convert miles to meters
            'limit': 5,  # Number of results to retrieve
            'open_now': True  # Filter for open businesses
        }

        try:
            response = requests.get('https://api.yelp.com/v3/businesses/search', headers=headers, params=params)
            data = response.json()

            if 'error' in data:
                print(f"Yelp API error: {data['error']['description']}")
                return []

            return [{'name': business['name'], 'rating': business.get('rating', 'N/A'), 'address': business['location'].get('address1', 'N/A')} for business in data.get('businesses', [])]

        except Exception as e:
            print(f"Error getting restaurant suggestions: {e}")
            return []

    def choose_random_restaurant(self):
        if self.restaurants_data:
            random_restaurant = random.choice(self.restaurants_data)
            restaurant_name = random_restaurant.get('name', 'N/A')
            restaurant_address = random_restaurant.get('address', 'N/A')
            self.result_label.config(text=f"Randomly Chosen Restaurant:\nName: {restaurant_name}\nAddress: {restaurant_address}")
        else:
            self.result_label.config(text="No restaurants available. Click 'Pick Food' first.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FoodPickerApp(root)
    root.mainloop()
