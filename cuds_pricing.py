import requests
import json
import time

from compute import data
from constants.regions import REGIONS


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

            # ######################################
            # Testing Purpose Only
            # ######################################
            # selected_machine_type["details"][region]["Hourly Cost"] = 0
            # selected_machine_type["details"][region]["Monthly Cost"] = 0
            # ######################################
            # Remove the above code
            # ######################################

        # print(f"Got the results : ", json.dumps(all_results, indent=4))
        # return
        print("Before Update \n\n")
        print("\n\n")
        all_cuds = []
        for product in all_results:
            product_prices = product.get("prices", [])
            print(product_prices)
            for prices in product_prices:
                print("pricesObj: ", prices)
                purchase_option = prices.get("purchaseOption", '')
                if purchase_option == "Commit1Yr" or purchase_option == 'Commit3Yr':
                    print("Product with CUDs price ", product)
                    all_cuds.append(product)
                continue

            print("hello")

        with open("constants/cuds.py", 'w') as file:
            file.write(f"cuds_pricing = {all_cuds} \n")
        time.sleep(30)
        return
        # if len(product_prices):
        #     sku = product.get("sku", "")
        #     productHash = product.get("productHash", "")
        #     selected_machine_type["sku"] = sku
        #     selected_machine_type["productHash"] = productHash
        #     product_prices = product.get("prices", [])
        #     if product_prices:
        #         selected_machine_type["details"][product["region"]
        #                                          ]["Hourly Cost"] = product_prices[0]["USD"]
        #         selected_machine_type["details"][product["region"]]["Monthly Cost"] = float(
        #             product_prices[0]["USD"])*730

        print("After Update \n\n")
        # print(f"\"{machine}\": ", json.dumps(data_clone[machine], indent=2))
        time.sleep(30)
        return
    else:
        print("Error in API Call")


update_prices()
