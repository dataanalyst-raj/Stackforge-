"""
StackForge - Location Database
Basic Wind Speed (IS 875 Part 3) + Seismic Zone (IS 1893)
"""

# Format: "City": {"wind_speed": m/s, "seismic_zone": "Zone X"}
LOCATION_DATA = {
    # North India
    "Haridwar": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Dehradun": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Rishikesh": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Delhi": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "New Delhi": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Noida": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Gurgaon": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Faridabad": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Ghaziabad": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Chandigarh": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Amritsar": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Ludhiana": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Jalandhar": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Jammu": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Srinagar": {"wind_speed": 39, "seismic_zone": "Zone 5"},
    "Shimla": {"wind_speed": 39, "seismic_zone": "Zone 4"},
    "Manali": {"wind_speed": 39, "seismic_zone": "Zone 4"},
    "Agra": {"wind_speed": 47, "seismic_zone": "Zone 3"},
    "Kanpur": {"wind_speed": 47, "seismic_zone": "Zone 3"},
    "Lucknow": {"wind_speed": 47, "seismic_zone": "Zone 3"},
    "Varanasi": {"wind_speed": 47, "seismic_zone": "Zone 3"},
    "Allahabad": {"wind_speed": 47, "seismic_zone": "Zone 3"},
    "Prayagraj": {"wind_speed": 47, "seismic_zone": "Zone 3"},
    "Bareilly": {"wind_speed": 47, "seismic_zone": "Zone 3"},
    "Meerut": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Roorkee": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Haldwani": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Nainital": {"wind_speed": 39, "seismic_zone": "Zone 4"},
    "Mussoorie": {"wind_speed": 39, "seismic_zone": "Zone 4"},

    # West India
    "Mumbai": {"wind_speed": 44, "seismic_zone": "Zone 3"},
    "Pune": {"wind_speed": 39, "seismic_zone": "Zone 3"},
    "Nagpur": {"wind_speed": 44, "seismic_zone": "Zone 2"},
    "Nashik": {"wind_speed": 39, "seismic_zone": "Zone 3"},
    "Aurangabad": {"wind_speed": 39, "seismic_zone": "Zone 2"},
    "Ahmedabad": {"wind_speed": 39, "seismic_zone": "Zone 3"},
    "Surat": {"wind_speed": 44, "seismic_zone": "Zone 3"},
    "Vadodara": {"wind_speed": 39, "seismic_zone": "Zone 3"},
    "Rajkot": {"wind_speed": 39, "seismic_zone": "Zone 3"},
    "Bhavnagar": {"wind_speed": 44, "seismic_zone": "Zone 3"},
    "Jamnagar": {"wind_speed": 44, "seismic_zone": "Zone 3"},
    "Gandhinagar": {"wind_speed": 39, "seismic_zone": "Zone 3"},
    "Goa": {"wind_speed": 39, "seismic_zone": "Zone 3"},
    "Panaji": {"wind_speed": 39, "seismic_zone": "Zone 3"},
    "Indore": {"wind_speed": 39, "seismic_zone": "Zone 2"},
    "Bhopal": {"wind_speed": 39, "seismic_zone": "Zone 2"},
    "Jabalpur": {"wind_speed": 39, "seismic_zone": "Zone 3"},
    "Gwalior": {"wind_speed": 47, "seismic_zone": "Zone 2"},
    "Ujjain": {"wind_speed": 39, "seismic_zone": "Zone 2"},
    "Raipur": {"wind_speed": 39, "seismic_zone": "Zone 2"},
    "Bhilai": {"wind_speed": 39, "seismic_zone": "Zone 2"},

    # South India
    "Chennai": {"wind_speed": 50, "seismic_zone": "Zone 3"},
    "Bangalore": {"wind_speed": 33, "seismic_zone": "Zone 2"},
    "Bengaluru": {"wind_speed": 33, "seismic_zone": "Zone 2"},
    "Hyderabad": {"wind_speed": 44, "seismic_zone": "Zone 2"},
    "Secunderabad": {"wind_speed": 44, "seismic_zone": "Zone 2"},
    "Coimbatore": {"wind_speed": 39, "seismic_zone": "Zone 3"},
    "Madurai": {"wind_speed": 39, "seismic_zone": "Zone 2"},
    "Tiruchirappalli": {"wind_speed": 39, "seismic_zone": "Zone 2"},
    "Salem": {"wind_speed": 39, "seismic_zone": "Zone 3"},
    "Tirunelveli": {"wind_speed": 39, "seismic_zone": "Zone 2"},
    "Kochi": {"wind_speed": 39, "seismic_zone": "Zone 3"},
    "Thiruvananthapuram": {"wind_speed": 39, "seismic_zone": "Zone 3"},
    "Kozhikode": {"wind_speed": 39, "seismic_zone": "Zone 3"},
    "Mangalore": {"wind_speed": 39, "seismic_zone": "Zone 3"},
    "Mysore": {"wind_speed": 33, "seismic_zone": "Zone 2"},
    "Hubli": {"wind_speed": 39, "seismic_zone": "Zone 2"},
    "Belgaum": {"wind_speed": 39, "seismic_zone": "Zone 3"},
    "Vijayawada": {"wind_speed": 50, "seismic_zone": "Zone 3"},
    "Visakhapatnam": {"wind_speed": 50, "seismic_zone": "Zone 2"},
    "Warangal": {"wind_speed": 44, "seismic_zone": "Zone 2"},
    "Tirupati": {"wind_speed": 39, "seismic_zone": "Zone 2"},
    "Pondicherry": {"wind_speed": 50, "seismic_zone": "Zone 2"},
    "Puducherry": {"wind_speed": 50, "seismic_zone": "Zone 2"},

    # East India
    "Kolkata": {"wind_speed": 50, "seismic_zone": "Zone 3"},
    "Howrah": {"wind_speed": 50, "seismic_zone": "Zone 3"},
    "Durgapur": {"wind_speed": 47, "seismic_zone": "Zone 3"},
    "Asansol": {"wind_speed": 47, "seismic_zone": "Zone 3"},
    "Siliguri": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Patna": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Gaya": {"wind_speed": 47, "seismic_zone": "Zone 3"},
    "Muzaffarpur": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Ranchi": {"wind_speed": 39, "seismic_zone": "Zone 2"},
    "Jamshedpur": {"wind_speed": 39, "seismic_zone": "Zone 2"},
    "Bhubaneswar": {"wind_speed": 50, "seismic_zone": "Zone 3"},
    "Cuttack": {"wind_speed": 50, "seismic_zone": "Zone 3"},
    "Rourkela": {"wind_speed": 39, "seismic_zone": "Zone 2"},
    "Guwahati": {"wind_speed": 50, "seismic_zone": "Zone 5"},
    "Shillong": {"wind_speed": 39, "seismic_zone": "Zone 5"},
    "Imphal": {"wind_speed": 39, "seismic_zone": "Zone 5"},
    "Aizawl": {"wind_speed": 39, "seismic_zone": "Zone 5"},
    "Agartala": {"wind_speed": 50, "seismic_zone": "Zone 5"},
    "Kohima": {"wind_speed": 39, "seismic_zone": "Zone 5"},
    "Itanagar": {"wind_speed": 39, "seismic_zone": "Zone 5"},
    "Gangtok": {"wind_speed": 39, "seismic_zone": "Zone 4"},
    "Darjeeling": {"wind_speed": 47, "seismic_zone": "Zone 4"},

    # Central & Other
    "Jaipur": {"wind_speed": 47, "seismic_zone": "Zone 2"},
    "Jodhpur": {"wind_speed": 47, "seismic_zone": "Zone 2"},
    "Udaipur": {"wind_speed": 47, "seismic_zone": "Zone 2"},
    "Kota": {"wind_speed": 47, "seismic_zone": "Zone 2"},
    "Ajmer": {"wind_speed": 47, "seismic_zone": "Zone 2"},
    "Bikaner": {"wind_speed": 47, "seismic_zone": "Zone 2"},
    "Alwar": {"wind_speed": 47, "seismic_zone": "Zone 2"},
    "Bhiwadi": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Panipat": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Karnal": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Hisar": {"wind_speed": 47, "seismic_zone": "Zone 2"},
    "Rohtak": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Sonipat": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Yamunanagar": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Ambala": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Saharanpur": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Moradabad": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Aligarh": {"wind_speed": 47, "seismic_zone": "Zone 3"},
    "Mathura": {"wind_speed": 47, "seismic_zone": "Zone 3"},
    "Firozabad": {"wind_speed": 47, "seismic_zone": "Zone 3"},
    "Jhansi": {"wind_speed": 47, "seismic_zone": "Zone 2"},
    "Gorakhpur": {"wind_speed": 47, "seismic_zone": "Zone 4"},
    "Faizabad": {"wind_speed": 47, "seismic_zone": "Zone 3"},
    "Ayodhya": {"wind_speed": 47, "seismic_zone": "Zone 3"},
}


def get_location_list():
    """Return sorted list of all location names."""
    return sorted(LOCATION_DATA.keys())


def get_location_data(location_name: str):
    """
    Return wind speed and seismic zone for a location.
    Returns None if location not found.
    """
    # Case-insensitive search
    for name, data in LOCATION_DATA.items():
        if name.lower() == location_name.lower():
            return data
    return None
