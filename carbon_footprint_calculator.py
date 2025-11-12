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

# Carbon footprint evaluation based on country
def get_country_thresholds(country):
    """
    Returns (good_threshold, excellent_threshold) in kg CO2 per year
    These are based on typical thresholds for developed countries
    """
    thresholds = {
        'usa': (6000, 4000),           # Higher threshold for USA
        'uk': (5000, 3500),            # Moderate threshold
        'germany': (4500, 3000),       # Lower threshold (more eco-conscious)
        'india': (3000, 1500),         # Lower threshold (developing country)
        'australia': (7000, 4500),     # Higher threshold (large country)
        'mexico': (4000, 2500),        # Moderate threshold
    }
    return thresholds.get(country.lower(), (5000, 3500))

def evaluate_footprint(yearly_total, country):
    """
    Evaluates carbon footprint using logical operators (and, or, not)
    Returns a tuple: (status, message)
    """
    good_threshold, excellent_threshold = get_country_thresholds(country)
    
    # Using logical operators for evaluation
    is_excellent = yearly_total <= excellent_threshold
    is_good = yearly_total <= good_threshold and not is_excellent
    is_poor = not (is_excellent or is_good)
    
    if is_excellent:
        status = "EXCELLENT"
        message = f"Outstanding! Your carbon footprint ({yearly_total:.2f} kg CO2/year) is well below the excellent threshold ({excellent_threshold} kg CO2/year) for {country}."
    elif is_good:
        status = "GOOD"
        message = f"Great! Your carbon footprint ({yearly_total:.2f} kg CO2/year) is within the good range for {country}. Keep it up!"
    else:
        status = "NEEDS IMPROVEMENT"
        reduction_needed = yearly_total - good_threshold
        message = f"Your carbon footprint ({yearly_total:.2f} kg CO2/year) is above the good threshold for {country}. Consider reducing your footprint by {reduction_needed:.2f} kg CO2/year."
    
    return status, message

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

    # Ask for country (5 options)
    country = ask_choice("Which country do you live in?", ['USA', 'UK', 'Germany', 'India', 'Australia', 'Mexico'])

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

    # Evaluate footprint based on country (convert to yearly if needed)
    yearly_total = total * 12 if period.lower() == 'monthly' else total
    status, message = evaluate_footprint(yearly_total, country)
    
    print(f"\n=== Carbon Footprint Evaluation for {country} ===")
    print(f"Status: {status}")
    print(f"Message: {message}")

    out_file = 'carbon_footprint_report.txt'
    df.to_csv(out_file, sep='\t', index=False, float_format='%.2f')
    print("\nReport exported to:", os.path.abspath(out_file))

if __name__ == "__main__":
    main()