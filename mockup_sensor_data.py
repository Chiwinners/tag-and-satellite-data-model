import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon

polygon_coords = [
    (-27.015380859374996, 50.28933925329178),
    (-25.960693359374996, -6.315298538330033),
    (-75.179443359375, -5.9657536710655235),
    (-79.046630859375, 7.36246686553575),
    (-98.382568359375, 20.3034175184893),
    (-99.437255859375, 31.952162238024975),
    (-84.320068359375, 33.7243396617476),
    (-74.827880859375, 43.58039085560784),
    (-53.031005859375, 49.61070993807422),
    (-27.015380859374996, 50.28933925329178)
]
poly = Polygon(polygon_coords)

n_samples = 1000
dt_hours = 1  # 1 hour step
time_hours = np.arange(0, n_samples*dt_hours, dt_hours)

# Create datetime starting at Jan 1, 2013
start_date = pd.Timestamp("2013-01-01 00:00:00")
dates = pd.date_range(start=start_date, periods=n_samples, freq=f"{dt_hours}H")

minx, miny, maxx, maxy = poly.bounds
latitudes = []
longitudes = []

while len(latitudes) < n_samples:
    rand_lon = np.random.uniform(minx, maxx)
    rand_lat = np.random.uniform(miny, maxy)
    if poly.contains(Point(rand_lon, rand_lat)):
        latitudes.append(rand_lat)
        longitudes.append(rand_lon)

latitudes = np.array(latitudes)
longitudes = np.array(longitudes)

pressure = np.random.normal(50, 20, n_samples).clip(0, None)
depth = pressure * 1.0197
temperature = np.random.normal(25, 2, n_samples) - 0.02*depth

accel = np.random.normal(0, 0.2, (n_samples, 3))
bursts = np.random.choice([0,1], size=n_samples, p=[0.98,0.02])
for i in range(3):
    accel[:,i] += bursts * np.random.normal(3, 1, n_samples)

vel = np.random.normal(0.5, 0.2, (n_samples, 3))
vel[bursts==1] += np.random.normal(1.5, 0.5, (sum(bursts), 3))

ph = np.random.normal(8.05, 0.05, n_samples)
mag = np.random.normal(50, 2, (n_samples, 3))
battery_soc = np.linspace(100, 20, n_samples) + np.random.normal(0, 1, n_samples)
capacitive = np.random.choice([0,1], size=n_samples, p=[0.995,0.005])

data = pd.DataFrame({
    "time_h": time_hours,
    "date": dates,
    "latitude": latitudes,
    "longitude": longitudes,
    "pressure_dbar": pressure,
    "depth_m": depth,
    "temperature_C": temperature,
    "accel_x": accel[:,0],
    "accel_y": accel[:,1],
    "accel_z": accel[:,2],
    "vel_x": vel[:,0],
    "vel_y": vel[:,1],
    "vel_z": vel[:,2],
    "pH": ph,
    "mag_x": mag[:,0],
    "mag_y": mag[:,1],
    "mag_z": mag[:,2],
    "battery_soc_%": battery_soc,
    "capacitive": capacitive
})

data.to_csv("shark_tag_mockup.csv", index=False)

print(data.head())


