import json

layout_data = {
    "project_info": {
        "sheet_id": "E-101",
        "title": "GENERATIVE MEP BLUEPRINT"
    },
    "mdb_location": [4800, 5000],
    "circuits": [
        {
            "cct_id": "P1",
            "type": "Power Ring",
            "layer": "E-POWR",
            "color": 1,
            "path_points": [[4800, 5000], [4800, 2100], [8500, 2100]]
        },
        {
            "cct_id": "LV1",
            "type": "IT Network (Cat6)",
            "layer": "E-DATA",
            "color": 5,
            "path_points": [[4800, 5000], [4800, 7000], [9100, 7000]]
        }
    ]
}

with open("layout_output.json", "w") as f:
    json.dump(layout_data, f, indent=2)

print("✅ Updated layout_output.json successfully!")