import requests
import json
import time
import os

from ..constants import REGIONS


def fetch_cuds_prices_from_infracost():
    """
    Fetches Commited Unit Discounts (CUDs) prices from the Infracost API and updates the CUDs dictionary.
    """
    print("Fetching CUDs prices from Infracost API...")
    all_regions = REGIONS

    query = """
        query {
            products(
            filter: {
                vendorName: "gcp",
                service: "Cloud SQL"
            },
            ) {
                productHash
                vendorName
                service
                productFamily
                region
                sku
                attributes {
                key
                value
                }
                prices {
                USD
                }
            }
        }
        """

    api_url = "https://pricing.api.infracost.io/graphql"

    headers = {
        'X-Api-Key': 'ico-tHZVHJcrKbucJ8Bg5nG0SSJGCIW29N9s',
        'Content-Type': 'application/json'
    }

    response = requests.post(api_url, headers=headers,
                             json={"query": query}, stream=True)
    print(response)
    if response.status_code == 200:
        all_results = response.json().get("data", {})

        all_cuds = {}
        service = ""
        tag = ""

        for product in all_results.get("products", []):
            for attribute in product.get("attributes", []):
                attribute_description = attribute.get("value", '')
                if "Cloud SQL for MySQL" in attribute_description:
                    service = "MySQL"
                    continue
                elif "Cloud SQL for PostgreSQL" in attribute_description:
                    service = "PostgreSQL"
                elif "Cloud SQL for SQL Server" in attribute_description:
                    service = "SQL"
                    continue
                if "Network" in attribute_description:
                    continue

                attribute_description_lst = attribute_description.split(":")
                print(attribute_description_lst)
                if len(attribute_description_lst) > 1:
                    tag = attribute_description_lst[1]
                if service and tag:
                    response_region = product.get("region", "")
                    usd_value = None
                    for price in product.get("prices", []):
                        usd_value = price.get("USD")

                    if response_region not in all_cuds:
                        all_cuds[response_region] = {}

                    if service not in all_cuds[response_region]:
                        all_cuds[response_region][service] = {}

                    print(response_region, service, tag)
                    all_cuds[response_region][service][tag] = usd_value
                    # if "1 year" in attribute_description:
                    #     all_cuds[response_region]["Commit1Yr"] = usd_value

                    # if "3 year" in attribute_description:
                    #     all_cuds[response_region]["Commit3Yr"] = usd_value

                    print("Product with CUDs price:", all_cuds)

        # Constructing the file path dynamically
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # constants_dir = os.path.join(current_dir, 'constants')
        cuds_file = os.path.join(
            current_dir, 'cloudSQL_cuds_infra_response.py')

        with open(cuds_file, 'w') as file:
            file.write(f"cuds_pricing = {all_cuds} \n")

        print("CUDs prices successfully updated.")
        time.sleep(30)  # Adding a delay to avoid overloading the API
    else:
        print("Error in API Call")


fetch_cuds_prices_from_infracost()
