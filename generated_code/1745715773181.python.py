```python
"""
Module: client_risk_categorization

This module provides a function to categorize a client as "Low", "Medium", or "High" risk based on
financial, operational, and compliance data. It also provides a display_result utility function.

Key Features:
- Robust type and value validation
- Handles missing data gracefully
- Dynamic risk score computation based on defined rules
- Boundary and edge case handling as per test requirements
"""

from typing import Dict, Any

def categorize_client(
    financial_data: Dict[str, Any],
    operational_data: Dict[str, Any],
    compliance_data: Dict[str, Any]
) -> str:
    """
    Categorize a client as 'Low', 'Medium', or 'High' risk based on input data.

    Parameters:
        financial_data (dict): Contains 'debt' (int/float) and 'revenue' (int/float).
        operational_data (dict): Contains 'incidents' (int).
        compliance_data (dict): Contains 'violations' (int).

    Returns:
        str: One of 'Low', 'Medium', or 'High' representing risk level.

    Raises:
        ValueError: If any required data is invalid (non-numeric or negative).
    """
    # Helper function for extracting and validating a numeric value
    def get_valid_number(d: Dict[str, Any], key: str, default: int = 0) -> int:
        val = d.get(key, default)
        if isinstance(val, (int, float)):
            # Only allow non-negative values for risk calculation
            if val < 0:
                raise ValueError(f"Negative value for '{key}': {val}")
            return int(val)
        elif val == "" or val is None:
            return default
        else:
            # Catch types like str or other invalids
            raise ValueError(f"Invalid type for '{key}': {type(val)} ({val})")
    
    # Extract and validate values (raise if invalid)
    debt = get_valid_number(financial_data, "debt")
    revenue = get_valid_number(financial_data, "revenue")
    incidents = get_valid_number(operational_data, "incidents")
    violations = get_valid_number(compliance_data, "violations")
    
    # Risk scoring logic:
    #   - Debt > 1,000,000: +2 points
    #   - Incidents > 5: +1 point
    #   - Violations > 0: +3 points
    risk_score = 0
    if debt > 1_000_000:
        risk_score += 2
    if incidents > 5:
        risk_score += 1
    if violations > 0:
        risk_score += 3

    # Assign risk levels based on score
    if risk_score >= 4:
        return "High"
    elif risk_score >= 2:
        return "Medium"
    else:
        return "Low"


def display_result(client_id: int, risk_level: str) -> str:
    """
    Format the display string for a client's risk level.

    Parameters:
        client_id (int): Unique identifier for the client.
        risk_level (str): Risk level string ("Low", "Medium", "High").

    Returns:
        str: Formatted display string.
    """
    return f"Client {client_id}: Risk Level - {risk_level}"

# No example usage block needed, as required functions are provided for testing purposes.
```
