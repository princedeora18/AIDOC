import requests
import time

# Predefined simple medication database
MEDICATIONS = {
    "bacterial": ["Amoxicillin", "Ciprofloxacin", "Azithromycin"],
    "viral, flu": ["Oseltamivir", "Zanamivir"],
    "fever": ["Acetaminophen", "Ibuprofen", "Naproxen"],
    "cold": ["Pseudoephedrine", "Dextromethorphan", "Guaifenesin"],
    "flu": ["Oseltamivir", "Acetaminophen", "Dextromethorphan"],
    "allergies": ["Loratadine", "Cetirizine", "Fluticasone"],
    "digestive issues (acid reflux)": ["Omeprazole", "Calcium Carbonate", "Magnesium Hydroxide"],
    "digestive issues (nausea)": ["Ondansetron", "Metoclopramide"],
    "digestive issues (diarrhea)": ["Loperamide"],
    "digestive issues (constipation)": ["Polyethylene Glycol", "Bisacodyl"],
    "pain relief": ["Acetaminophen", "Ibuprofen", "Tramadol"],
    "inflammation": ["Ibuprofen", "Naproxen", "Prednisone"],
    "hypertension": ["Lisinopril", "Amlodipine", "Hydrochlorothiazide"],
    "diabetes": ["Metformin", "Insulin", "Glipizide"],
    "skin conditions (acne)": ["Benzoyl Peroxide", "Tretinoin", "Doxycycline"],
    "skin conditions (eczema)": ["Hydrocortisone", "Tacrolimus"],
    "skin conditions (fungal)": ["Clotrimazole"]
}


# Function to get latitude & longitude from location
def get_location_coordinates(location):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": location, "format": "json", "limit": 1}
    headers = {"User-Agent": "SimpleHospitalFinder/1.0"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()

        if not data:
            print("❌ No location data found. Please try another city or zip code.")
            return None, None

        return float(data[0]["lat"]), float(data[0]["lon"])

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching location: {e}")
        return None, None


# Function to get hospitals near given location
def get_nearby_hospitals(location, radius=5000):
    lat, lon = get_location_coordinates(location)

    if lat is None or lon is None:
        return []

    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    node["amenity"="hospital"](around:{radius},{lat},{lon});
    out;
    """

    headers = {"User-Agent": "SimpleHospitalFinder/1.0"}

    try:
        response = requests.post(overpass_url, data={"data": overpass_query}, headers=headers, timeout=10)
        hospitals = response.json().get("elements", [])

        if not hospitals:
            print(f"⚠️ No hospitals found within {radius}m of {location}.")
            return []

        hospital_list = []
        for hospital in hospitals[:5]:  # Get top 5 hospitals
            name = hospital.get("tags", {}).get("name", "Unnamed Hospital")
            address = hospital.get("tags", {}).get("addr:full", "Address not available")
            contact = hospital.get("tags", {}).get("phone", "Not available")

            hospital_list.append({"name": name, "address": address, "contact": contact})

        return hospital_list

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching hospitals: {e}")
        return []


# Function to get medications for a disease
def get_medications(disease):
    disease = disease.lower()
    return MEDICATIONS.get(disease, ["No specific medications found. Consult a doctor."])


# Main function to run the program
def main():
    print("\n🏥 Welcome to the Disease & Hospital Finder! 🏥\n")

    while True:
        # Ask for disease
        disease = input("💊 Enter your disease (e.g., diabetes, flu, cough) or type 'exit' to quit: ").strip()
        if disease.lower() == "exit":
            print("👋 Exiting... Stay healthy!")
            break

        # Ask for location
        location = input("🔍 Enter your location (city/zip) or type 'exit' to quit: ").strip()
        if location.lower() == "exit":
            print("👋 Exiting... Stay healthy!")
            break

        # Ask for search radius
        radius_input = input("📏 Enter search radius in meters (default 5000m): ").strip()
        radius = int(radius_input) if radius_input.isdigit() else 5000

        print("\n⏳ Searching for hospitals... Please wait...\n")
        hospitals = get_nearby_hospitals(location, radius)

        # Display hospitals
        if hospitals:
            print(f"✅ Top hospitals near {location}:")
            print("=" * 50)
            for idx, hospital in enumerate(hospitals, 1):
                print(f"{idx}. {hospital['name']}")
                print(f"   📍 Address: {hospital['address']}")
                print(f"   📞 Contact: {hospital['contact']}\n")

        # Display medications
        print(f"💊 Recommended medications for {disease.capitalize()}:")
        print("-" * 50)
        for med in get_medications(disease):
            print(f"✔️ {med}")

        print("\n🔹 Always consult a doctor before taking any medication.\n")
        time.sleep(1)  # Small delay to respect API limits


if __name__ == "__main__":
    main()
