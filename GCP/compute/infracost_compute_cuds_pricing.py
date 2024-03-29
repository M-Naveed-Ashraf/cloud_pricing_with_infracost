import requests
import json
import time
import os

from .constants.utils import REGIONS
from .constants.utils import all_machine_series


def create_dict_from_infracost_response(response_object, all_cuds_dict, purchase_option):
    """
    Extracts relevant information from the response_object and constructs a dictionary of Commited Unit Discounts (CUDs).

    Args:
        response_object (dict): The response object received from the Infracost API.
        all_cuds_dict (dict): Dictionary containing Commited Unit Discounts (CUDs).
        purchase_option (str): The purchase option for the resource.

    Returns:
        dict: Updated dictionary of Commited Unit Discounts (CUDs).
    """
    machine_series = None
    resource_group = None
    usd_value = None
    region = response_object.get("region", "")
    all_cuds_dict_clone = all_cuds_dict.copy()

    for attribute in response_object.get("attributes", []):
        if attribute.get("key") == "resourceGroup":
            resource_group = attribute.get("value")

        if attribute.get("key") == "description":
            description = attribute.get("value", "").lower()
            for series in all_machine_series:
                if series in description:
                    machine_series = series
                    break

    for price in response_object.get("prices", []):
        usd_value = price.get("USD")

    if machine_series and resource_group and region and usd_value:
        if machine_series in all_cuds_dict_clone:
            if region not in all_cuds_dict_clone[machine_series]:
                all_cuds_dict_clone[machine_series][region] = {}
            if purchase_option not in all_cuds_dict_clone[machine_series][region]:
                all_cuds_dict_clone[machine_series][region][purchase_option] = {
                }
            all_cuds_dict_clone[machine_series][region][purchase_option][resource_group] = usd_value
        else:
            all_cuds_dict_clone[machine_series] = {
                region: {purchase_option: {resource_group: usd_value}}}

    return all_cuds_dict_clone


def fetch_cuds_prices_from_infracost():
    """
    Fetches Commited Unit Discounts (CUDs) prices from the Infracost API and updates the CUDs dictionary.
    """
    print("Fetching CUDs prices from Infracost API...")
    all_regions = REGIONS

    graphql_query = []

    for region in all_regions:
        updated_region = region.replace("-", "_")
        alias = f"products_{updated_region}"
        query = (
            f"{alias}: products(filter: {{ vendorName: \"gcp\", service: \"Compute Engine\", "
            f"region: \"{region}\", productFamily: \"Compute\", "
            f"}})  "
            f"{{ productHash vendorName service productFamily region sku  "
            f"attributes {{ key value }}  "
            f"prices {{ USD unit description purchaseOption }} "
            f"}}"
        )

        graphql_query.append(query)

    batch_query = json.dumps({
        "query": f"query {{ {' '.join(graphql_query)} }}",
    })

    api_url = "https://pricing.api.infracost.io/graphql"

    headers = {
        'X-Api-Key': 'ico-tHZVHJcrKbucJ8Bg5nG0SSJGCIW29N9s',
        'Content-Type': 'application/json'
    }

    response = requests.post(api_url, headers=headers,
                             data=batch_query, stream=True)

    if response.status_code == 200:
        all_results = []

        for region in all_regions:
            updated_region = region.replace("-", "_")
            alias = f"products_{updated_region}"
            results_for_alias = response.json().get("data", {}).get(alias, [])
            all_results.extend(results_for_alias)

        all_cuds = {}
        for product in all_results:
            for prices in product.get("prices", []):
                purchase_option = prices.get("purchaseOption", '')
                if purchase_option in ["Commit1Yr", "Commit3Yr", "Preemptible"]:
                    all_cuds = create_dict_from_infracost_response(
                        product, all_cuds, purchase_option)
                    print("Product with CUDs price:", all_cuds)

        all_cuds_response = json.dumps(
            all_cuds, indent=2)
        # Constructing the file path dynamically
        current_dir = os.path.dirname(os.path.abspath(__file__))
        constants_dir = os.path.join(current_dir, 'constants')
        new_data_file = os.path.join(
            constants_dir, "cuds.py")
        with open(new_data_file, 'w') as file:
            file.write(f"cuds_pricing = {all_cuds_response} \n")

        print("CUDs prices successfully updated.")
        time.sleep(30)  # Adding a delay to avoid overloading the API
    else:
        print("Error in API Call ", response.text)


fetch_cuds_prices_from_infracost()
