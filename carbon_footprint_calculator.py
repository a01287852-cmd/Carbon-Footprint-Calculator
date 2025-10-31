import numpy as np
import pandas as pd
import os

# Emission factors (kg CO2 per unit)
energy_factors = np.array([0.233, 5.3, 2.31])  # electricity (kWh), gas (therms), fuel (liters)
transport_factors = {'car': 0.21, 'bus': 0.11, 'train': 0.05, 'bike': 0.0}  # kg CO2 per km
water_factors = 0.344  # kg CO2 per m3
waste_factors = 0.21   # kg CO2 per kg of waste (approximate)
diet_factors = {'omnivore': 200.0, 'vegetarian': 100.0, 'vegan': 70.0}  # kg CO2 per month

def get_energy_footprint(electricity_kwh, gas_therms, fuel_liters):
    usage = np.array([electricity_kwh, gas_therms, fuel_liters])
    return float(np.sum(energy_factors * usage))

def get_transport_footprint(distance_km, transport_type):
    factor = transport_factors.get(transport_type, 0.0)
    return float(distance_km * factor)

def get_water_footprint(water_m3):
    return float(water_m3 * water_factors)

def get_waste_footprint(waste_kg):
    return float(waste_kg * waste_factors)

def get_diet_footprint(diet_type):
    return float(diet_factors.get(diet_type, 0.0))

# Validation of input

def ask_float(prompt):
    """
    Ask for a non-negative float. Repeat until a valid non-negative number is entered.
    Accepts blank input as 0. Uses logical operators to validate finiteness and non-negativity.
    """
    while True:
        try:
            raw = input(prompt).strip()
            if raw == '':
                value = 0.0
            else:
                value = float(raw)
            # Use logical operators: not (finite) OR negative -> reject
            if (not np.isfinite(value)) or (value < 0):
                print("Please enter a non-negative finite number.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number.")

def ask_choice(prompt, choices):
    choices_str = '/'.join(choices)
    while True:
        value = input(f"{prompt} ({choices_str}): ").strip().lower()
        if value in choices:
            return value
        print(f"Please choose from: {choices_str}")

def ask_yesno(prompt):
    """
    Accepts 'yes', 'y', 'no', 'n'. Demonstrates OR for multiple accepted values.
    """
    val = ask_choice(prompt, ['yes', 'no', 'y', 'n'])
    return (val == 'yes') or (val == 'y')

# Questions and calculations to approximate your Carbon Footprint

def main():
    print("=== Carbon Footprint Calculator ===")

    # Monthly usage inputs
    electricity_kwh = ask_float("Approximate your monthly electricity usage (kWh) — enter 0 if unknown: ")
    gas_therms = ask_float("Approximate your monthly gas usage (therms) — enter 0 if unknown: ")
    fuel_liters = ask_float("Approximate your monthly fuel usage (liters) — enter 0 if unknown: ")
    energy = get_energy_footprint(electricity_kwh, gas_therms, fuel_liters)

    transport_type = ask_choice("Enter your main transport type", ['car', 'bus', 'train', 'bike'])
    distance_km = ask_float("Approximate your monthly distance traveled by this transport (km): ")
    transport = get_transport_footprint(distance_km, transport_type)

    water_m3 = ask_float("Approximate your monthly water usage (cubic meters) — enter 0 if unknown: ")
    water = get_water_footprint(water_m3)

    waste_kg = ask_float("Approximate your monthly waste produced (kg) — enter 0 if unknown: ")
    waste = get_waste_footprint(waste_kg)

    diet_type = ask_choice("Choose your diet type", list(diet_factors.keys()))
    diet = get_diet_footprint(diet_type)

    # Monthly vs Yearly
    period = ask_choice("Would you like the report monthly or yearly", ['monthly', 'yearly'])
    multiplier = 12 if period == 'yearly' else 1

    categories = {
        'Energy': energy * multiplier,
        'Transport': transport * multiplier,
        'Water': water * multiplier,
        'Waste': waste * multiplier,
        'Diet': diet * multiplier
    }

    df = pd.DataFrame(list(categories.items()), columns=['Category', 'CO2_kg'])
    total = df['CO2_kg'].sum()
    df.loc[len(df)] = ['Total', total]

    
   # Format CO2 numbers to 2 decimal places for readability (keeps numeric dtype for calculations)
    df['CO2_kg'] = df['CO2_kg'].round(2)

    # Display and export
    print(f"\n=== Your Carbon Footprint Report ({period.capitalize()}) ===")
    print(df.to_string(index=False))

    out_path = 'carbon_footprint_report.txt'
    df.to_csv(out_path, sep='\t', index=False)
    print("\nReport exported to:", os.path.abspath(out_path))
    
    # Visual report
    
    try:
        import matplotlib.pyplot as plt
        # Exclude Total from the plot
        plot_df = df[df['Category'] != 'Total']
        plt.figure(figsize=(8, 4))
        bars = plt.bar(plot_df['Category'], plot_df['CO2_kg'], color=['#2b8cbe', '#a6bddb', '#7fbf7b', '#fdae61', '#d7191c'])
        plt.title(f"Carbon Footprint by Category ({period.capitalize()})")
        plt.ylabel("kg CO2")
        plt.tight_layout()
        # Annotate values
        for bar in bars:
            height = bar.get_height()
            plt.annotate(f"{height:.2f}", xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 4), textcoords="offset points", ha='center', va='bottom', fontsize=8)
        chart_path = 'carbon_footprint_chart.png'
        plt.savefig(chart_path, dpi=150)
        print("Chart saved to:", os.path.abspath(chart_path))
        # Try to show the plot (will open a window if available)
        if ask_yesno("Open chart now?"):
            plt.show()
        plt.close()
    except ImportError:
        print("matplotlib not installed — skipping visual report. Install it with: pip install matplotlib")

if __name__ == "__main__":
    main()
