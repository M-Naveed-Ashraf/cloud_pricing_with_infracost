## Files:

It consists of three main files:

1. **get_cuds_prices.py:**
   This file contains functions to calculate the pricing based on Commited Unit Discounts (CUDs) for different regions, and purchase options. It includes the following components:

   - `calculate_cuds_price(region, purchase_option)`: Function to calculate the CUDs price for a region, and purchase option.
   - `output_1yr` and `output_3yr`: Example usage of `calculate_cuds_price` to demonstrate pricing for different purchase options.

2. **kubernetes_cuds.py:**
   This file stores the pricing data for Commited Unit Discounts (CUDs) organized by region, and purchase option. It is used by `get_cuds_prices.py` to fetch pricing information for calculations.

3. **infracost_cuds_pricing.py:**
   This file contains functionality to fetch pricing data from the Infracost API and update the pricing information stored in `kubernetes_cuds.py`. It can be run as a scheduler to periodically update the prices.

## Usage:

To use the pricing calculator:

1. Ensure that the necessary pricing data is stored in `kubernetes_cuds.py`.
2. Run `python3 GCP/kubernetes/get_cuds_prices.py` from the root folder.
3. Provide the desired machine type, region, and purchase option (Commit1Yr, Commit3Yr).
4. The script will calculate and display the hourly and monthly costs based on CUDs pricing.

To fetch the prices from infracost

1. Remove the data in `kubernetes_cuds.py`
2. Run the file as a module `python3 -m GCP.kubernetes.fetch_infracost_cuds_pricing` from the root folder.
3. After successful run check the `kubernetes_cuds.py` if populated.
