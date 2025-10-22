import numpy as np
import pandas as pd
import os

# Emission factors (kg CO2 per unit)

def get_energy_footprint(electricity_kwh, gas_therms, fuel_liters):
    factors = np.array([0.233, 5.3, 2.31])
    usage = np.array([electricity_kwh, gas_therms, fuel_liters])
    return np.sum(factors * usage)

# Transport emission factors (kg CO2 per km)

def get_transport_footprint(distance_km, transport_type):
    transport_factors = {'car': 0.21, 'bus': 0.11, 'train': 0.05, 'bike': 0.0}
    factor = transport_factors.get(transport_type, 0)
    return distance_km * factor

# User input functions

def ask_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid number.")

# Choice input function

def ask_choice(prompt, choices):
    choices_str = '/'.join(choices)
    while True:
        value = input(f"{prompt} ({choices_str}): ").strip().lower()
        if value in choices:
            return value
        print(f"Please choose from: {choices_str}")

# Main function

def main():
    print("=== Carbon Footprint Calculator ===")

    # Ask for their energy, gas, fuel and electricity usage:

    electricity_kwh = ask_float("Approximate your monthly electricity usage (kWh): ")
    gas_therms = ask_float("Approximate your monthly gas usage (therms): ")
    fuel_liters = ask_float("Approximate your monthly fuel usage (liters): ")
    energy = get_energy_footprint(electricity_kwh, gas_therms, fuel_liters)

    # Ask for their transport type and distance traveled:

    transport_type = ask_choice("Enter your main transport type", ['car', 'bus', 'train', 'bike'])
    distance_km = ask_float("Approximate your monthly distance traveled by this transport (km): ")
    transport = get_transport_footprint(distance_km, transport_type)
    
    # Compile results into a DataFrame and export to a text file

    data = {
        'Energy': energy,
        'Transport': transport,
    }
    df = pd.DataFrame(list(data.items()), columns=['Category', 'CO2_kg'])
    total = df['CO2_kg'].sum()
    df.loc[len(df)] = ['Total', total]

    # Display and export the report

    print("\n=== Your Carbon Footprint Report ===")
    print(df)
    df.to_csv('carbon_footprint_report.txt', sep='\t', index=False)
    print("\nReport exported to:", os.path.abspath('carbon_footprint_report.txt'))

if __name__ == "__main__":
    main()
