# get_cuds_prices.py

from compute import data
from constants.cuds import cuds_pricing


from typing import Optional, Dict, Literal


def get_compute_cuds(machine_type: Optional[str] = None, region: str = None, cpu: Optional[str | int] = None, memory: Optional[str | int] = None, machine_series: Optional[(Literal["n2", "a2", "t2d", "m3", "c3", "h3", "e2", "g2", "c2"] | None)] = None) -> Dict[str, float]:

    if not machine_type and not cpu and not memory and not machine_series:
        raise ValueError(
            "At least one of machine_type, cpu, or memory must be provided.")

    machine_details = None
    cpu_used = None
    memory_used = None

    if machine_type:
        machine_details = data[machine_type]["details"].get(region)
        machine_series = machine_details["Series"].lower()
        cpu_used = float(machine_details["vCPUs"])
        memory_used = float(machine_details["Memory"])
    elif cpu and memory and machine_series:
        machine_series = machine_series
        cpu_used = float(cpu)
        memory_used = float(memory)
    else:
        raise ValueError(
            "Either machine_type or both cpu and memory must be provided.")

    if machine_series and cpu_used and memory_used:

        cuds_cpu_price_1y = float(
            cuds_pricing[machine_series][region]["Commit1Yr"]["CPU"])
        cuds_ram_price_1y = float(
            cuds_pricing[machine_series][region]["Commit1Yr"]["RAM"])

        hourly_cost = cpu_used * cuds_cpu_price_1y + memory_used * cuds_ram_price_1y
        monthly_cost_1y = hourly_cost * 730  # Assuming 730 hours in a month

        cuds_cpu_price_3y = float(
            cuds_pricing[machine_series][region]["Commit3Yr"]["CPU"])
        cuds_ram_price_3y = float(
            cuds_pricing[machine_series][region]["Commit3Yr"]["RAM"])

        hourly_cost = cpu_used * cuds_cpu_price_3y + memory_used * cuds_ram_price_3y
        monthly_cost_3y = hourly_cost * 730  # Assuming 730 hours in a month

        return {
            "Commit1Yr": round(monthly_cost_1y, 2),
            "Commit3Yr": round(monthly_cost_3y, 2)
        }
    else:
        return {
            "Commit1Yr": -1,
            "Commit3Yr": -1
        }


output = get_compute_cuds(machine_series="e2", cpu=2,
                          memory=4, region="us-central1")
print(output)
