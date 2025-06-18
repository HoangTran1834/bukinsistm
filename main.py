import requests
import json

def create_time_matrix(locations):
    """
    Calls Valhalla's sources_to_targets API to build a time matrix.
    'locations' is a list of {"lon": lon, "lat": lat} dicts.
    The first location should be the depot (điểm xuất phát).
    """
    valhalla_url = "http://localhost:8002/sources_to_targets"
    
    # Valhalla expects lists of sources and targets
    request_data = {
        "sources": locations,
        "targets": locations,
        "costing": "auto",
        "costing_options": {
            "auto": {
                "country_crossing_penalty": 2000.0 # You can adjust costing options
            }
        }
    }
    
    headers = {'Content-type': 'application/json'}
    
    try:
        response = requests.post(valhalla_url, data=json.dumps(request_data), headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes
        
        results = response.json()
        print("[DEBUG] Valhalla API raw response:", results)
        # Nếu Valhalla trả về dict, lấy đúng trường chứa ma trận
        if isinstance(results, dict) and 'sources_to_targets' in results:
            items = results['sources_to_targets']
        else:
            items = results

        num_locations = len(locations)
        time_matrix = [[0] * num_locations for _ in range(num_locations)]

        # Flatten nếu items là list các list
        flat_items = []
        for sub in items:
            if isinstance(sub, list):
                flat_items.extend(sub)
            else:
                flat_items.append(sub)

        for item in flat_items:
            print(f"[DEBUG] Processing item: {item}")
            if isinstance(item, dict) and 'from_index' in item and 'to_index' in item:
                from_idx = item['from_index']
                to_idx = item['to_index']
                time_matrix[from_idx][to_idx] = int(item['time'])
            else:
                print(f"[WARNING] Unexpected item in Valhalla response: {item}")
            
        return time_matrix
        
    except requests.exceptions.RequestException as e:
        print(f"Error calling Valhalla API: {e}")
        return None
    
    
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def solve_vrp(data):
    """Solves the Capacitated VRP with Pickups and Deliveries."""
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # --- 1. Define Cost of Travel ---
    def time_callback(from_index, to_index):
        """Returns the travel time between the two nodes."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['time_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # --- 2. Add Capacity Constraint ---
    def demand_callback(from_index):
        """Returns the demand of the node."""
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')
        
    # --- 3. Define Pickup & Delivery Requests ---
    for request in data['pickups_deliveries']:
        pickup_index = manager.NodeToIndex(request[0])
        delivery_index = manager.NodeToIndex(request[1])
        routing.AddPickupAndDelivery(pickup_index, delivery_index)
        routing.solver().Add(
            routing.VehicleVar(pickup_index) == routing.VehicleVar(delivery_index))

    # --- 4. Setting search parameters and solve ---
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(5)

    solution = routing.SolveWithParameters(search_parameters)
    
    # --- 5. Print solution ---
    if solution:
        print_solution(data, manager, routing, solution)


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print(f'Objective (tổng thời gian tối thiểu của tất cả các xe): {solution.ObjectiveValue()}s')
    total_time = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = f'Lộ trình cho xe {vehicle_id}:\n'
        route_time = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data['demands'][node_index]
            plan_output += f' {node_index} (Tải: {route_load}) -> '
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_time += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += f'{manager.IndexToNode(index)}\n'
        plan_output += f'Tổng thời gian của lộ trình: {route_time}s\n'
        
        # Sửa lại phần in tải tối đa
        capacity_dimension = routing.GetDimensionOrDie("Capacity")
        start_load = solution.Value(capacity_dimension.CumulVar(routing.Start(vehicle_id)))
        end_load = solution.Value(capacity_dimension.CumulVar(routing.End(vehicle_id)))
        max_load = max(start_load, end_load)
        plan_output += f'Tải tại điểm đầu: {start_load}, tải tại điểm cuối: {end_load}\n'
        plan_output += f'Tải tối đa trên xe: {max_load}\n'
        
        print(plan_output)
        total_time += route_time
    print(f'Tổng thời gian di chuyển của tất cả các xe: {total_time}s')


if __name__ == '__main__':
    # --- DATA PREPARATION ---
    all_locations = [
        {"lat": 16.080, "lon": 108.230},  # 0: Depot (điểm xuất phát chung)
        {"lat": 16.074, "lon": 108.222},  # 1: Đón khách A
        {"lat": 16.060, "lon": 108.223},  # 2: Đón khách B
        {"lat": 16.045, "lon": 108.210},  # 3: Đón khách C
        {"lat": 16.065, "lon": 108.235},  # 4: Đón khách D
        {"lat": 15.567, "lon": 108.483},  # 5: Trả khách A
        {"lat": 15.572, "lon": 108.479},  # 6: Trả khách B
        {"lat": 15.560, "lon": 108.490},  # 7: Trả khách C
        {"lat": 15.580, "lon": 108.470},  # 8: Trả khách D
    ]

    time_matrix_from_valhalla = create_time_matrix(all_locations)
    if time_matrix_from_valhalla:
        all_passenger_pairs = [[1, 5], [2, 6], [3, 7], [4, 8]]
        num_vehicles = 2  # Số xe
        vehicle_capacity = 7

        print(f"Bắt đầu phân bổ {len(all_passenger_pairs)} khách cho {num_vehicles} xe.")
        print("=====================================================")

        for i in range(num_vehicles):
            passengers_for_this_vehicle = all_passenger_pairs[i::num_vehicles]
            if not passengers_for_this_vehicle:
                print(f"Xe {i} không có khách nào được phân bổ.")
                continue
            print(f"\n--- Giải bài toán cho Xe {i} với {len(passengers_for_this_vehicle)} khách ---")
            data = {}
            data['time_matrix'] = time_matrix_from_valhalla
            data['pickups_deliveries'] = passengers_for_this_vehicle
            data['num_vehicles'] = 1
            data['vehicle_capacities'] = [vehicle_capacity]
            data['depot'] = 0
            demands = [0] * len(all_locations)
            for pickup, delivery in passengers_for_this_vehicle:
                demands[pickup] = 1
                demands[delivery] = -1
            data['demands'] = demands
            solve_vrp(data)

