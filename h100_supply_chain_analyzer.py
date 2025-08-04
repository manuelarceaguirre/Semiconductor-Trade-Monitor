#!/usr/bin/env python3
"""
H100 Supply Chain Flow Analyzer
Analyzes the H100 supply chain CSV to extract actual supply chain flows
based on ships_to_next relationships.
"""

import csv
import json
from typing import Dict, List, Any

def parse_h100_supply_chain():
    """Parse H100 supply chain CSV and extract actual flows."""
    
    # Read and parse the CSV file
    nodes = {}
    flows = []
    
    csv_path = "/home/manuel/semiconductormonitor/data/h100/h100.csv"
    
    with open(csv_path, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        
        # First pass: collect all nodes
        for row in reader:
            node_id = row['node_id']
            nodes[node_id] = {
                'node_id': node_id,
                'parent_id': row['parent_id'] if row['parent_id'] != 'NULL' else None,
                'depth': int(row['depth']) if row['depth'] else 0,
                'tier': row['tier'],
                'subpart_category': row['subpart_category'],
                'primary_output': row['primary_output'],
                'company': row['company'],
                'facility_name': row['facility_name'],
                'city': row['city'],
                'state_province': row['state_province'],
                'country': row['country'],
                'lat': float(row['lat']) if row['lat'] and row['lat'] != '–' else None,
                'lon': float(row['lon']) if row['lon'] and row['lon'] != '–' else None,
                'is_raw_material': row['is_raw_material'] == 'TRUE',
                'ships_to_next': row['ships_to_next'] if row['ships_to_next'] else None
            }
    
    # Second pass: create flows based on ships_to_next relationships
    for node_id, node in nodes.items():
        if node['ships_to_next'] and node['ships_to_next'] in nodes:
            destination_node = nodes[node['ships_to_next']]
            
            # Only create flow if both nodes have valid coordinates
            if (node['lat'] is not None and node['lon'] is not None and 
                destination_node['lat'] is not None and destination_node['lon'] is not None):
                
                flow = {
                    'from_city': node['city'],
                    'from_country': node['country'],
                    'from_lat': node['lat'],
                    'from_lon': node['lon'],
                    'to_city': destination_node['city'],
                    'to_country': destination_node['country'],
                    'to_lat': destination_node['lat'],
                    'to_lon': destination_node['lon'],
                    'commodity': node['primary_output'],
                    'company': node['company'],
                    'from_facility': node['facility_name'],
                    'to_facility': destination_node['facility_name'],
                    'tier_from': node['tier'],
                    'tier_to': destination_node['tier'],
                    'depth_from': node['depth'],
                    'depth_to': destination_node['depth'],
                    'is_raw_material': node['is_raw_material']
                }
                flows.append(flow)
    
    return flows, nodes

def generate_h100_supply_chain_json():
    """Generate the JSON structure for H100 supply chain flows."""
    
    flows, nodes = parse_h100_supply_chain()
    
    # Create the final JSON structure
    supply_chain_data = {
        'metadata': {
            'description': 'NVIDIA H100 SXM5 80GB Supply Chain Flows',
            'source': 'Actual supply chain mapping based on ships_to_next relationships',
            'total_flows': len(flows),
            'total_nodes': len(nodes),
            'date_analyzed': '2025-08-02'
        },
        'flows': flows
    }
    
    return supply_chain_data

def main():
    """Main function to analyze H100 supply chain and output JSON."""
    
    print("Analyzing H100 Supply Chain CSV...")
    
    supply_chain_data = generate_h100_supply_chain_json()
    
    print(f"Found {supply_chain_data['metadata']['total_flows']} actual supply chain flows")
    print(f"Total nodes in supply chain: {supply_chain_data['metadata']['total_nodes']}")
    
    # Output the JSON
    json_output = json.dumps(supply_chain_data, indent=2)
    print("\n" + "="*80)
    print("H100 SUPPLY CHAIN FLOWS JSON:")
    print("="*80)
    print(json_output)
    
    # Also save to file for reference
    with open('/home/manuel/semiconductormonitor/h100_supply_chain_flows.json', 'w') as f:
        f.write(json_output)
    
    print(f"\nJSON also saved to: /home/manuel/semiconductormonitor/h100_supply_chain_flows.json")

if __name__ == '__main__':
    main()