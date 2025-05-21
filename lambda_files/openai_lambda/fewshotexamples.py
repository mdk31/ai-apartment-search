
text0 = "Show me listings in Brooklyn under $2000"
output0 = {
    "select": ["listings.id", "listings.address", "listings.price"],
    "from": ["listings"],
    "where": [
        {"column": "listings.price", "operator": "<", "value": 2000},
        {"column": "listings.neighborhood", "operator": "=", "value": "Brooklyn"}
    ]
}

text1 = "Find affordable listings in low crime areas near Prospect Heights"
output1 = {
    "select": ["listings.id", "listings.address", "listings.price"],
    "from": ["listings"],
    "joins": [
        {
            "type": "left",
            "table": "nypd_complaints",
            "on": {
                "name": "ST_DWithin",
                "args": ["listings.geom", "nypd_complaints.geom", 250]
            }
        }
    ],
    "where": [
        {"column": "listings.price", "operator": "<", "value": 2500},
        {"column": "listings.neighborhood", "operator": "=", "value": "Prospect Heights"}
    ],
    "group_by": ["listings.id", "listings.address", "listings.price"],
    "having": [
        {
            "aggregate": "COUNT",
            "column": "nypd_complaints.id",
            "operator": "<",
            "value": 3
        }
    ]
}