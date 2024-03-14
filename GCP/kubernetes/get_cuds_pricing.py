# get_cuds_prices.py

from kubernetes_cuds import cuds_pricing


def calculate_cuds_price(region, purchase_option):
    """
    Calculates the price of Commited Unit Discounts (CUDs) for a given machine type, region, and purchase option.

    Args:
        region (str): The region where the kubernetes engine is located.
        purchase_option (str): The purchase option for the kubernetes.

    Returns:
        tuple: A tuple containing the details of the hourly and monthly costs.
    """

    hourly_cost = float(cuds_pricing[region][purchase_option])
    monthly_cost = hourly_cost * 730  # Assuming 730 hours in a month
    return (
        float(hourly_cost),
        float(monthly_cost),
    )


# Example usage
output_1yr = calculate_cuds_price("us-central1", "Commit1Yr")
output_3yr = calculate_cuds_price("us-central1", "Commit3Yr")

print("1-year CUDs price:", output_1yr)
print("3-year CUDs price:", output_3yr)
