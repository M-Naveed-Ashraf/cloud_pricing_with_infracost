
import requests
import json
import os

# from .constants.utils import REGIONS
from .compute import data


def update_prices():
    print("Function Start")
    data_clone = data
    all_machine_types = data.keys()

    for machine in all_machine_types:
        # all_regions = data["a2-highgpu-1g"]["details"].keys()
        selected_machine_type = data_clone[machine]
        all_regions = selected_machine_type["details"].keys()

        graphql_query = []

        print("selected machine: ", machine)

        # Making a batch query for all regions to run in one api call
        for region in all_regions:
            updated_region = region.replace("-", "_")
            alias = f"products_{updated_region}"
            query = f"{alias}: products(filter: {{ vendorName: \"gcp\", service: \"Compute Engine\", region: \"{region}\", attributeFilters: [{{ key: \"machineType\", value: \"{machine}\" }}] }}) {{ productHash vendorName service productFamily region sku attributes {{ key value }} prices {{ USD unit description purchaseOption }} }}"

            graphql_query.append(query)
            print(
                f"Query is ready and appended in batch query for alis: \"{alias}\"")

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

        response = requests.post(url=api_url, headers=headers,
                                 data=batch_query, stream=True)

        if response.status_code == 200:
            all_results = []

            for region in all_regions:
                updated_region = region.replace("-", "_")
                alias = f"products_{updated_region}"
                results_for_alias = response.json().get("data", {}).get(alias, [])
                all_results.extend(results_for_alias)  # Concatenate the lists

            print(f"Got the results for \"{machine}\" : ", json.dumps(
                all_results, indent=4))

            print("Before Update \n\n")
            print(f"\"{machine}\": ", json.dumps(
                data_clone[machine], indent=2))
            print("\n\n")
            # time.sleep(30)
            for product in all_results:
                attributes = product.get("attributes", "")
                for attribute in attributes:
                    machine_type = attribute.get("key", "")
                    machine_type_value = attribute.get("value", "")
                    if machine_type_value == machine:
                        sku = product.get("sku", "")
                        productHash = product.get("productHash", "")
                        selected_machine_type["sku"] = sku
                        selected_machine_type["productHash"] = productHash
                        product_prices = product.get("prices", [])
                        if product_prices:
                            if product_prices[0]["purchaseOption"] == "on_demand":
                                selected_machine_type["details"][product["region"]
                                                                 ]["Hourly Cost"] = product_prices[0]["USD"]
                                selected_machine_type["details"][product["region"]]["Monthly Cost"] = float(
                                    product_prices[0]["USD"])*730
                            if product_prices[1]["purchaseOption"] == "preemptible":
                                selected_machine_type["details"][product["region"]
                                                                 ]["Hourly Cost preemptible"] = product_prices[1]["USD"]
                                selected_machine_type["details"][product["region"]]["Monthly Cost preemptible"] = float(
                                    product_prices[1]["USD"])*730

            print("After Update \n\n")
            print(f"\"{machine}\": ", json.dumps(
                data_clone[machine], indent=2))

            data_clone_response = json.dumps(
                data_clone, indent=2)

            # Constructing the file path dynamically
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # constants_dir = os.path.join(current_dir, 'constants')
            new_data_file = os.path.join(
                current_dir, 'new_compute_data.py')
            with open(new_data_file, 'w') as file:
                file.write(f"new_compute_data = {data_clone_response} \n")

            print("CUDs prices successfully updated.")
            # Result is in data_clone
            # print(data_clone)

        else:
            print(response.text)


update_prices()
