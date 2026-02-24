def get_procurement_data(medicine_name):
    """Generates deep-links for PharmEasy procurement[cite: 36, 48]."""
    # In a full version, this would map to a Generic Medicine database [cite: 24]
    base_url = "https://pharmeasy.in/search/all?searchTextField="
    return {
        "generic_mapping_available": True,
        "potential_savings": "70%",
        "buy_link": f"{base_url}{medicine_name.replace(' ', '%20')}"
    }