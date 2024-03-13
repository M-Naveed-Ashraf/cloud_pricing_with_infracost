import requests
import json
import time

from compute import data
from constants.regions import REGIONS
from constants.all_machine_types import all_machine_series


def fetch_machine_series_prices(response_object, all_cuds_dict={}):
    machine_series = None
    resource_group = None
    usd_value = None
    region = response_object.get("region", "")
    temp_dict = all_cuds_dict

    for attribute in response_object.get("attributes", []):
        if attribute.get("key") == "resourceGroup":
            resource_group = attribute.get("value")

        if attribute.get("key") == "description":
            description = attribute.get("value", "")
            description = description.lower()
            for series in all_machine_series:
                if series in description:
                    machine_series = series
                    break

    for price in response_object.get("prices", []):
        usd_value = price.get("USD")

    # If all required data is available, construct the output
    if machine_series and resource_group and region and usd_value:
        # Check if the machine series already exists in all_cuds
        if machine_series in temp_dict:
            # Update the existing machine series object with the new region and its prices
            if region not in temp_dict[machine_series]:
                temp_dict[machine_series][region] = {}
            temp_dict[machine_series][region][resource_group] = usd_value
        else:
            # If machine series does not exist, create a new entry for it in all_cuds
            temp_dict[machine_series] = {region: {resource_group: usd_value}}

    return temp_dict


def update_prices():
    print("Function Start")
    data_clone = data
    all_regions = REGIONS

    graphql_query = []

    # Making a batch query for all regions to run in one api call
    for region in all_regions:
        updated_region = region.replace("-", "_")
        alias = f"products_{updated_region}"
        query = f"{alias}: products(filter: "\
            f"{{ vendorName: \"gcp\", service: \"Compute Engine\", "\
            f"region: \"{region}\", productFamily: \"Compute\",  "\
            f"}})  "\
            f"{{ productHash vendorName service productFamily region sku  "\
            f"attributes {{ key value }}  "\
            f"prices {{ USD unit description purchaseOption }} "\
            f"}}"

        graphql_query.append(query)
        print(
            f"Query is ready and appended in batch query for alias: \"{alias}\"")

    batch_query = json.dumps({
        "query": f"query {{ {' '.join(graphql_query)} }}",
    })

    # print("query for API: ", batch_query)
    print("Batch query is ready and Calling API")

    api_url = "https://pricing.api.infracost.io/graphql"

    headers = {
        'X-Api-Key': 'ico-tHZVHJcrKbucJ8Bg5nG0SSJGCIW29N9s',
        'Content-Type': 'application/json'
    }

    response = requests.request(
        "POST", api_url, headers=headers, data=batch_query, stream=True)

    if response.status_code == 200:
        all_results = []

        for region in all_regions:
            updated_region = region.replace("-", "_")
            alias = f"products_{updated_region}"
            results_for_alias = response.json().get("data", {}).get(alias, [])
            all_results.extend(results_for_alias)  # Concatenate the lists

        print("Before Update \n\n")
        print("\n\n")
        all_cuds = {}
        for product in all_results:
            product_prices = product.get("prices", [])
            print(product_prices)
            for prices in product_prices:
                print("pricesObj: ", prices)
                purchase_option = prices.get("purchaseOption", '')
                if purchase_option == "Commit1Yr" or purchase_option == 'Commit3Yr':
                    # print("Product with CUDs price ", product)
                    output = fetch_machine_series_prices(product, all_cuds)
                    print("Product with CUDs price ", output)
                    all_cuds = output
                continue

            print("hello")

        with open("constants/cuds.py", 'w') as file:
            file.write(f"cuds_pricing = {all_cuds} \n")
        print("After Update \n\n")
        time.sleep(30)
        return
    else:
        print("Error in API Call")


update_prices()
