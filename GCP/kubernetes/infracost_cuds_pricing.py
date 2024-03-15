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

    graphql_query = []

    for region in all_regions:
        updated_region = region.replace("-", "_")
        alias = f"products_{updated_region}"
        query = (
            f"{alias}: products(filter: {{ vendorName: \"gcp\", service: \"Kubernetes Engine\", "
            f"region: \"{region}\" "
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
                if purchase_option in ["Commit1Yr", "Commit3Yr"]:
                    response_region = product.get("region", "")
                    usd_value = prices.get("USD", None)

                    if response_region not in all_cuds:
                        all_cuds[response_region] = {}
                    all_cuds[response_region][purchase_option] = usd_value

                    print("Product with CUDs price:", all_cuds)

        # Constructing the file path dynamically
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # constants_dir = os.path.join(current_dir, 'constants')
        cuds_file = os.path.join(current_dir, 'kubernetes_cuds.py')

        with open(cuds_file, 'w') as file:
            file.write(f"cuds_pricing = {all_cuds} \n")

        print("CUDs prices successfully updated.")
        time.sleep(30)  # Adding a delay to avoid overloading the API
    else:
        print("Error in API Call")


fetch_cuds_prices_from_infracost()
