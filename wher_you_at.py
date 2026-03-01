import pandas as pd


known_base_lat = 12.990123
known_base_lon = 80.223452


df = pd.read_csv("dgps_rover_data.csv")


corrected_lat = []
corrected_lon = []


for i in range(len(df)):
   lat_correction = known_base_lat - df["Base Latitude (Measured)"][i]
   lon_correction = known_base_lon - df["Base Longitude (Measured)"][i]


   corrected_lat.append(df["Rover Latitude (Measured)"][i] + lat_correction)
   corrected_lon.append(df["Rover Longitude (Measured)"][i] + lon_correction)


df["Corrected Rover Latitude"] = corrected_lat
df["Corrected Rover Longitude"] = corrected_lon


df.to_csv("dgps_rover_data.csv", index=False)
pd.set_option('display.max_columns', None)
print(df[["Rover Latitude (Measured)", "Rover Longitude (Measured)", "Corrected Rover Latitude", "Corrected Rover Longitude"]])
