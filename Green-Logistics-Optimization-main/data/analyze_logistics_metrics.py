import pandas as pd
import matplotlib.pyplot as plt
import os

# === File Paths ===
WORLD_EDGE_FILE = "world/world_edges.txt"
VEHICLE_FILE = "vehicles copy.csv"
EMISSION_LOOKUP_FILE = "co2_emissions.csv"
OUTPUT_DIR = "analysis_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Step 1: Load data ===
edges_df = pd.read_csv(WORLD_EDGE_FILE, sep="\t")
vehicles_df = pd.read_csv(VEHICLE_FILE)
emissions_df = pd.read_csv(EMISSION_LOOKUP_FILE)

# === Step 2: Map Fuel Type codes ===
FUEL_TYPE_MAP = {
    1: "X",  # Gasoline
    2: "Z",  # Diesel
    3: "E",  # Ethanol
    4: "D",  # Electricity
    5: "N",  # Natural Gas
    6: "B",  # Hybrid (or custom type, adjust as needed)
}

vehicles_df["Fuel Type"] = vehicles_df["Fuel Type"].map(FUEL_TYPE_MAP).astype(str)
emissions_df["Fuel Type"] = emissions_df["Fuel Type"].astype(str)

# === Step 3: Merge for CO₂ emission values ===
merged = vehicles_df.merge(
    emissions_df,
    on=["Engine Size(L)", "Cylinders", "Fuel Type"],
    how="left"
)

# Fill missing emission values with average
avg_emission = emissions_df["CO2 Emissions(g/km)"].mean()
merged["CO2 Emissions(g/km)"].fillna(avg_emission, inplace=True)
vehicles_df["CO2 Emissions(g/km)"] = merged["CO2 Emissions(g/km)"]

# === Step 4: Estimate emissions for each edge ===
# For now, assume Vehicle ID 1 used across all edges
vehicle_emission_rate = vehicles_df.iloc[0]["CO2 Emissions(g/km)"]  # grams/km

edges_df["Distance_km"] = edges_df["distance"] / 1000  # convert meters to km
edges_df["CO2_grams"] = edges_df["Distance_km"] * vehicle_emission_rate
edges_df["Duration_min"] = edges_df["duration"] / 60  # convert seconds to minutes

# === Step 5: Aggregate metrics ===
total_distance = edges_df["Distance_km"].sum()
total_duration = edges_df["Duration_min"].sum()
total_emissions = edges_df["CO2_grams"].sum()

print("=== Logistics Metrics Summary ===")
print(f"Total Distance     : {total_distance:.2f} km")
print(f"Total Duration     : {total_duration:.2f} minutes")
print(f"Total CO₂ Emission : {total_emissions:.2f} grams")

# === Step 6: Plot ===
metrics = {
    "Distance (km)": total_distance,
    "Duration (min)": total_duration,
    "Emissions (g CO₂)": total_emissions
}

plt.figure(figsize=(8, 4))
plt.bar(metrics.keys(), metrics.values(), color=["#4CAF50", "#2196F3", "#FF5722"])
plt.ylabel("Value")
plt.title("Green Logistics Summary Metrics")
plt.tight_layout()
plot_path = os.path.join(OUTPUT_DIR, "logistics_metrics_summary.png")
plt.savefig(plot_path)
plt.show()

print(f"\n📊 Plot saved to: {plot_path}")
