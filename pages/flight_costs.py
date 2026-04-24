import pandas as pd
import streamlit as st
from serpapi import GoogleSearch
import time

api_key = st.secrets["SERP_API_KEY"]
outbound_date = "2026-07-01"
return_date = "2026-07-08"
origin_id = "LHR"

destinations = {
    "Berlin": "BER",
    "Ibiza": "IBZ",
    "Marrakech": "RAK",
    "Reykjavik": "KEF",
    "Kyoto": "KIX",
    "Rio de Janeiro": "GIG",
    "Bali": "DPS",
    "Cape Town": "CPT",
    "Banff": "YYC",
    "Tulum": "CUN"
}

@st.cache_data
def get_flight_data(dest_name, dest_code, direct_only=False):
    params = {
        "engine": "google_flights",
        "departure_id": origin_id,
        "arrival_id": dest_code,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "type": "1",
        "currency": "GBP",
        "hl": "en",
        "stops": "0" if direct_only else "2",
        "api_key": api_key,
        "deep_search": True
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            print(f"API Error for {dest_name}: {results['error']}")
        
        flights = results.get("best_flights", []) + results.get("other_flights", [])
        
        if not flights:
            print(f"No flights found for {dest_name}")
            return None
        
        cheapest = min(flights, key=lambda x: x.get("price", 999999))
        
        # Get all flight segments
        all_legs = cheapest.get("flights", [])
        outbound_leg = all_legs[0] if len(all_legs) > 0 else {}
        
        # SAFETY CHECK: Only grab return_leg if it exists
        if len(all_legs) > 1:
            return_leg = all_legs[1]
            return_time = return_leg.get("departure_airport", {}).get("time", "N/A")
        else:
            return_leg = {}
            return_time = "Unknown" 

        return {
            "City": dest_name,
            "Airport_Code": dest_code,
            "Price_GBP": cheapest.get("price"),
            "Outbound_Date": outbound_date,
            "Outbound_Time": outbound_leg.get("departure_airport", {}).get("time"),
            "Return_Date": return_date,
            "Return_Time": return_time,
            "Outbound_Departure": outbound_leg.get("departure_airport", {}).get("time"), 
            "Outbound_Arrival": outbound_leg.get("arrival_airport", {}).get("time"),
            "Duration_Mins": outbound_leg.get("duration"),
            "Airline": outbound_leg.get("airline"),
            "Departure_Airport": outbound_leg.get("departure_airport", {}).get("id")
        }
    except Exception as e:
        print(f"Error fetching {dest_name}: {e}")
        return None

# --- EXECUTION LOOP ---
results_list = []

print("Starting API data collection (this will take a few minutes)...")

for city, code in destinations.items():
    print(f"Fetching data for {city}...")
    data = get_flight_data(city, code, False)
    if data:
        results_list.append(data)
    time.sleep(1)

# --- SAVE TO CSV ---
if results_list:
    df = pd.DataFrame(results_list)
    filename = "holiday_flight_prices.csv"
    df.to_csv(filename, index=False)
    print(f"\n✅ SUCCESS! File saved as: {filename}")
    print(df)
else:
    print("\n❌ No data was collected.")
    
   
    
   