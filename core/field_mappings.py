# core/field_mappings.py

COMMON_NAMES = {
    "vessel_name": "vessel_name",
    "ata": "ata",
    "atd": "atd",
    "eta": "eta",
    "etd": "etd",
    "operator": "operator",
    "status": "status",
    "voyage_number": "voyage_number"
}


FIELD_MAPPINGS = {
    "dpworld": {
        "VesselName": COMMON_NAMES["vessel_name"],
        "ATA": COMMON_NAMES["ata"],
        "ATD": COMMON_NAMES["atd"],
        "ETA": COMMON_NAMES["eta"],
        "ETD": COMMON_NAMES["etd"],
        "Line_Operator": COMMON_NAMES["operator"],
        "Phase": COMMON_NAMES["status"],
        "VoyageNo": COMMON_NAMES["voyage_number"]
    },
    # Add more site mappings here
    "webapps": {
        "VesselName": COMMON_NAMES["vessel_name"],
        "ATA": COMMON_NAMES["ata"],
        "ATD": COMMON_NAMES["atd"],
        "ETA": COMMON_NAMES["eta"],
        "ETD": COMMON_NAMES["etd"],
        "Operator": COMMON_NAMES["operator"],
        "InVoyage": COMMON_NAMES["voyage_number"]
    },
    
}
