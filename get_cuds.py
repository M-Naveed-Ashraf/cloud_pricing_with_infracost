from compute import data
from constants.cuds import cuds_pricing


def get_cuds_price(machine_type, region):
    machine_details = data[machine_type]["details"][region]
    if machine_details:
        machine_series = machine_details["Series"].lower()
        cpu_used = float(machine_details["vCPUs"])
        memory_used = float(machine_details["Memory"])

        cuds_cpu_price = float(cuds_pricing[machine_series][region]["CPU"])
        cuds_ram_price = float(cuds_pricing[machine_series][region]["RAM"])
        print("Cuds for selected machine ",
              cuds_pricing[machine_series][region])

        hourly_cost = cpu_used * cuds_cpu_price + memory_used * cuds_ram_price
        monthly_cost = hourly_cost * 730
        return (
            machine_details["vCPUs"],
            machine_details["Memory"],
            float(hourly_cost),
            float(monthly_cost),
        )


output = get_cuds_price("e2-medium", "us-central1")
print(output)
