#Used AI for the measurement conversions
#and to help get the bounding box data

import geopandas as gpd
import pandas as pd

#1 square mile in square meters, used to convert projected areas into the
#same units as the CENSUSAREA attribute (square miles).
SQM_PER_SQMI = 2589988.11

gdf = gpd.read_file("gz_2010_us_050_00_20m.shp")


bounds = gdf.bounds
gdf["Bounding box Coordinates"] = list(
    zip(bounds["minx"], bounds["miny"], bounds["maxx"], bounds["maxy"])
)

#Reproject to an equal-area CRS so bounding-box width * height is a
#real area, then convert from square meters to square miles to match
#the units of CENSUSAREA.
gdf_equal_area = gdf.to_crs("EPSG:5070")
proj_bounds = gdf_equal_area.bounds
bbox_area_sqmi = (
    (proj_bounds["maxx"] - proj_bounds["minx"])
    * (proj_bounds["maxy"] - proj_bounds["miny"])
) / SQM_PER_SQMI
gdf["B-box Area"] = bbox_area_sqmi

#Occupied column as requested for the assignment
gdf["Occupied"] = (
    gdf["CENSUSAREA"] / gdf["B-box Area"]
)

#Cleaning up the visuals and changing column names to be more readable
df = gdf.set_index(["STATE", "COUNTY"]).sort_index()
df.rename(columns={"CENSUSAREA": "Census Area","NAME": "Name","GEO_ID": "ID"}, inplace=True)
df.index.set_names(["State#", "County#"], inplace=True)

#Dropped the actual coordinates and geometry when printing as they aren't very readable and take up a lot of space
HIDDEN_COLUMNS = ["geometry", "Bounding box Coordinates"]

#State filter section
#Lets the user look up a single state by its number (FIPS code)

#The shapefile only stores state numbers, so this maps each number to a name
#so the user can look up specific states easier
STATE_FIPS = {
    "01": "Alabama", "02": "Alaska", "04": "Arizona", "05": "Arkansas",
    "06": "California", "08": "Colorado", "09": "Connecticut", "10": "Delaware",
    "11": "District of Columbia", "12": "Florida", "13": "Georgia", "15": "Hawaii",
    "16": "Idaho", "17": "Illinois", "18": "Indiana", "19": "Iowa",
    "20": "Kansas", "21": "Kentucky", "22": "Louisiana", "23": "Maine",
    "24": "Maryland", "25": "Massachusetts", "26": "Michigan", "27": "Minnesota",
    "28": "Mississippi", "29": "Missouri", "30": "Montana", "31": "Nebraska",
    "32": "Nevada", "33": "New Hampshire", "34": "New Jersey", "35": "New Mexico",
    "36": "New York", "37": "North Carolina", "38": "North Dakota", "39": "Ohio",
    "40": "Oklahoma", "41": "Oregon", "42": "Pennsylvania", "44": "Rhode Island",
    "45": "South Carolina", "46": "South Dakota", "47": "Tennessee", "48": "Texas",
    "49": "Utah", "50": "Vermont", "51": "Virginia", "53": "Washington",
    "54": "West Virginia", "55": "Wisconsin", "56": "Wyoming", "72": "Puerto Rico",
}

#Reverse lookup so a state name can be typed instead of a number
NAME_TO_FIPS = {name.lower(): fips for fips, name in STATE_FIPS.items()}


def find_state_fips(user_text):
    """Turn what the user typed into a two-digit state number, or None if no match."""
    text = user_text.strip().lower()
    if text.isdigit():
        #Accepts "1" or "01" and pads it to match the shapefile format
        fips = text.zfill(2)
        return fips if fips in STATE_FIPS else None
    return NAME_TO_FIPS.get(text)


while True:
    choice = input("\nEnter a state number or name, 'all' for every county, or press Enter to quit: ")
    if choice.strip() == "":
        break

    #Typing "all" prints the full table for every state
    if choice.strip().lower() == "all":
        print(f"\nAll states - {len(df)} counties\n")
        print(df.drop(columns=HIDDEN_COLUMNS, errors="ignore").to_string())
        continue

    fips = find_state_fips(choice)
    if fips is None:
        print(f"'{choice}' didn't match a state. Try a number like 37 or a name like North Carolina.")
        continue

    state_df = df[df.index.get_level_values("State#") == fips]
    if state_df.empty:
        print(f"No counties found for {STATE_FIPS[fips]}.")
        continue

    print(f"\n{STATE_FIPS[fips]} (State# {fips}) - {len(state_df)} counties\n")
    print(state_df.drop(columns=HIDDEN_COLUMNS, errors="ignore").to_string())