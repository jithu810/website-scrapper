# core/field_mappings.py
COMMON_NAMES = {
    "vessel_name": "vessel_name",
    "ata": "ata",
    "atd": "atd",
    "eta": "eta",
    "etd": "etd",
    "operator": "operator",
    "status": "status",
    "voyage_number": "voyage_number",
    "berth_position":"berth_position",
    "cargo_type":"cargo_type"
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
    "webapps_abudhabi": {
        "VesselName": COMMON_NAMES["vessel_name"],
        "ATA": COMMON_NAMES["ata"],
        "ATD": COMMON_NAMES["atd"],
        "ETA": COMMON_NAMES["eta"],
        "ETD": COMMON_NAMES["etd"],
        "Operator": COMMON_NAMES["operator"],
        "InVoyage": COMMON_NAMES["voyage_number"]
    },
    "salalahport": {
        "Vessel": COMMON_NAMES["vessel_name"],
        "ATA": COMMON_NAMES["ata"],
        "ATD": COMMON_NAMES["atd"],
        "ETA": COMMON_NAMES["eta"],
        "ETD": COMMON_NAMES["etd"],
        "Line": COMMON_NAMES["operator"],
        "Status": COMMON_NAMES["status"],
        "Rotation#": COMMON_NAMES["voyage_number"]
    },
    "fujairahport": {
        "Vessel_name": COMMON_NAMES["vessel_name"],
        "Arrival Date": COMMON_NAMES["eta"],
        "Sailing Date": COMMON_NAMES["etd"],
        "Voy-No": COMMON_NAMES["voyage_number"],
        "Agent": COMMON_NAMES["operator"],
        "Berth position": COMMON_NAMES['berth_position'], 
        "Cargo Type": COMMON_NAMES["cargo_type"],          
        "Arrival Time":COMMON_NAMES['ata'], # Can be mapped as ATA
        "Sailing Time": COMMON_NAMES['atd'] # Can be mapped as ATD
    }
}
