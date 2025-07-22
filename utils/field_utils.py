from core.mappings.field_mappings_port import FIELD_MAPPINGS as PORT_FIELD_MAPPING
from core.mappings.field_mappings_port import COMMON_NAMES as PORT_COMMON_NAMES
from core.mappings.field_mappings_vessel import FIELD_MAPPINGS as VESSAL_FIELD_MAPPING 
from core.mappings.field_mappings_vessel import COMMON_NAMES as VESSEL_COMMON_NAMES 
from utils.config import Config

loggers = Config.init_logging()
service_logger = loggers['chatservice']

def map_rows_by_site(site_id: str, all_rows: list[dict],mapping_type) -> list[dict]:
    """
    Maps keys in each row of data to standardized keys using FIELD_MAPPINGS for a given site.
    Fills missing common fields with None and logs the mapping process.

    Args:
        site_id (str): The ID of the site to determine the mapping.
        all_rows (list[dict]): List of dictionaries representing raw scraped rows.

    Returns:
        list[dict]: A list of dictionaries with standardized keys. Missing fields filled with None.
    """
    if mapping_type=="vessel":
        service_logger.info("selected mapping type VESSEL")
        mapping_json=VESSAL_FIELD_MAPPING
        common_name=VESSEL_COMMON_NAMES
    else:
        service_logger.info("selected mapping type PORT")
        mapping_json=PORT_FIELD_MAPPING
        common_name=PORT_COMMON_NAMES
        
    mapping = mapping_json.get(site_id, {})
    standard_keys = set(common_name.values())
    if not mapping:
        service_logger.warning(f"⚠️ No field mapping found for site: {site_id}. Raw rows will remain unmapped.")
    mapped_rows = []
    for idx, row in enumerate(all_rows):
        mapped_row = {
            standard_key: row.get(original_key, "")
            for original_key, standard_key in mapping.items()
        }

        missing_keys = []
        for key in standard_keys:
            if key not in mapped_row:
                mapped_row[key] = None
                missing_keys.append(key)

        if missing_keys:
            service_logger.debug(
                f"Row {idx+1}: Missing fields filled with None: {missing_keys}"
            )

        mapped_rows.append(mapped_row)

    service_logger.info(
        f" Mapping complete for site '{site_id}'. Total rows mapped: {len(mapped_rows)}"
    )
    return mapped_rows
