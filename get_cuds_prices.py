# get_cuds_prices.py

from compute import data
from constants.cuds import cuds_pricing

def calculate_cuds_price(machine_type, region, purchase_option):
    """
    Calculates the price of Compute Unit Discounts (CUDs) for a given machine type, region, and purchase option.

    Args:
        machine_type (str): The type of the machine.
        region (str): The region where the machine is located.
        purchase_option (str): The purchase option for the machine.

    Returns:
        tuple: A tuple containing the details of the machine and the calculated hourly and monthly costs.
    """
    machine_details = data[machine_type]["details"].get(region)
    
    if machine_details:
        machine_series = machine_details["Series"].lower()
        cpu_used = float(machine_details["vCPUs"])
        memory_used = float(machine_details["Memory"])

        cuds_cpu_price = float(cuds_pricing[machine_series][region][purchase_option]["CPU"])
        cuds_ram_price = float(cuds_pricing[machine_series][region][purchase_option]["RAM"])

        hourly_cost = cpu_used * cuds_cpu_price + memory_used * cuds_ram_price
        monthly_cost = hourly_cost * 730  # Assuming 730 hours in a month
        return (
            machine_details["vCPUs"],
            machine_details["Memory"],
            float(hourly_cost),
            float(monthly_cost),
        )
    else:
        return None

# Example usage
output_1yr = calculate_cuds_price("e2-medium", "us-central1", "Commit1Yr")
output_3yr = calculate_cuds_price("e2-medium", "us-central1", "Commit3Yr")

print("1-year CUDs price:", output_1yr)
print("3-year CUDs price:", output_3yr)
