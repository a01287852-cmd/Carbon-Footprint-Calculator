import numpy as np
import pandas as pd
import os

# Emission factors (kg CO2 per unit)
# Energy: electricity (kg CO2 per kWh), gas (kg CO2 per therm), fuel (kg CO2 per liter)
def get_energy_footprint(electricity_kwh, gas_therms, fuel_liters):
    factors = np.array([0.233, 5.3, 2.31])
    usage = np.array([electricity_kwh, gas_therms, fuel_liters])
    return float(np.sum(factors * usage))

# Transport emission factors (kg CO2 per km)
def get_transport_footprint(distance_km, transport_type):
    transport_factors = {'car': 0.21, 'bus': 0.11, 'train': 0.05, 'bike': 0.0}
    factor = transport_factors.get(transport_type, 0.0)
    return float(distance_km * factor)

# Water footprint (kg CO2 per cubic meter)
def get_water_footprint(water_m3):
    factor = 0.344
    return float(water_m3 * factor)

# Diet footprint using approximate average daily kg CO2 per person:
def get_diet_footprint(diet_type, days_per_month=30):
    daily_factors = {'omnivore': 7.2, 'vegetarian': 3.8, 'vegan': 2.9}
    daily = daily_factors.get(diet_type, 5.0)
    return float(daily * days_per_month)

# Waste footprint (kg CO2 per kg waste) -- estimate
def get_waste_footprint(waste_kg):
    factor = 0.21
    return float(waste_kg * factor)

# User input functions
def ask_float(prompt, allow_negative=False):
    while True:
        try:
            value = float(input(prompt))
            if not allow_negative and value < 0:
                print("Please enter a non-negative number.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number.")

# Choice input function
def ask_choice(prompt, choices):
    choices_lower = [c.lower() for c in choices]
    choices_str = '/'.join(choices)
    while True:
        value = input(f"{prompt} ({choices_str}): ").strip().lower()
        if value in choices_lower:
            # return the canonical choice from original list (preserve case if needed)
            return choices[choices_lower.index(value)]
        print(f"Please choose from: {choices_str}")

def main():
    print("=== Carbon Footprint Calculator ===\n")

    # Ask for monthly energy usage (inputs are monthly)
    electricity_kwh = ask_float("Approximate your monthly electricity usage (kWh): ")
    gas_therms = ask_float("Approximate your monthly gas usage (therms): ")
    fuel_liters = ask_float("Approximate your monthly fuel usage (liters): ")
    energy = get_energy_footprint(electricity_kwh, gas_therms, fuel_liters)

    # Transport
    transport_type = ask_choice("Enter your main transport type", ['car', 'bus', 'train', 'bike'])
    distance_km = ask_float("Approximate your monthly distance traveled by this transport (km): ")
    transport = get_transport_footprint(distance_km, transport_type)

    # Additional categories: water, diet, waste
    water_m3 = ask_float("Approximate your monthly household water use (cubic meters): ")
    water = get_water_footprint(water_m3)

    diet_type = ask_choice("Select your diet type", ['omnivore', 'vegetarian', 'vegan'])
    diet = get_diet_footprint(diet_type)

    waste_kg = ask_float("Approximate your monthly household waste (kg): ")
    waste = get_waste_footprint(waste_kg)

    # Aggregate monthly results
    monthly_data = {
        'Energy': energy,
        'Transport': transport,
        'Water': water,
        'Diet': diet,
        'Waste': waste,
    }

    # Ask whether to show monthly or yearly estimates
    period = ask_choice("Show results as", ['monthly', 'yearly'])
    multiplier = 1 if period.lower() == 'monthly' else 12

    data = {k: float(v * multiplier) for k, v in monthly_data.items()}
    df = pd.DataFrame(list(data.items()), columns=['Category', 'CO2_kg'])
    df['CO2_kg'] = df['CO2_kg'].round(2)
    total = df['CO2_kg'].sum()
    df.loc[len(df)] = ['Total', round(total, 2)]

    # Display and export the report
    print(f"\n=== Your Carbon Footprint Report ({period.capitalize()}) ===")
    print(df.to_string(index=False))

    out_file = 'carbon_footprint_report.txt'
    df.to_csv(out_file, sep='\t', index=False, float_format='%.2f')
    print("\nReport exported to:", os.path.abspath(out_file))

if __name__ == "__main__":
    main()