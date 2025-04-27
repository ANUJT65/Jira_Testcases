```python
"""
risk_scoring.py

This module provides a single function `categorize_client_risk` to assess and categorize
the risk profile of a client based on their 'financial', 'operational', and 'compliance' parameters.
It is robust to missing data, non-integer inputs, negative and out-of-range values, and 
applies proper data normalization and error handling as inferred from the provided test cases.

Risk categories:
- "Low": score < 40
- "Medium": 40 <= score < 70
- "High": score >= 70

The scoring formula:
    score = 0.5 * financial + 0.3 * operational + 0.2 * compliance

Each parameter is normalized to [0, 100] (negative values clamped to 0, values above 100 capped at 100).

Author: [Your Name]
"""

from typing import Dict, Any

def categorize_client_risk(client_data: Dict[str, Any]) -> str:
    """
    Categorizes a client into 'Low', 'Medium', or 'High' risk based on provided parameters.

    Parameters
    ----------
    client_data : dict
        Dictionary containing any of the keys: 'financial', 'operational', 'compliance'.
        Values can be int, float, or str representing numbers.
        Missing keys are treated as 0. Invalid/non-convertible values are treated as 0.
        Negative values are clamped to 0, values above 100 are capped at 100.

    Returns
    -------
    str
        One of "Low", "Medium", "High" representing the risk category.

    Raises
    ------
    None. Handles all edge cases gracefully.

    Examples
    --------
    >>> categorize_client_risk({'financial': 40, 'operational': 40, 'compliance': 40})
    'Medium'
    """
    # Define weights and keys
    WEIGHTS = {
        'financial': 0.5,
        'operational': 0.3,
        'compliance': 0.2,
    }
    PARAM_KEYS = list(WEIGHTS.keys())

    def _parse_value(val: Any) -> float:
        """
        Convert input value to float, safely handling strings and invalid data.
        Clamp negative values to 0, cap values above 100 to 100.
        Invalid values (e.g., None, non-numeric strings) are treated as 0.
        """
        try:
            # If value is a string, try to convert
            if isinstance(val, str):
                val = float(val.strip())
            # If value is int or float
            elif isinstance(val, (int, float)):
                val = float(val)
            else:
                # Unrecognized type, treat as 0
                return 0.0
        except (ValueError, TypeError):
            return 0.0
        # Clamp to [0, 100]
        if val < 0:
            return 0.0
        if val > 100:
            return 100.0
        return val

    # Extract and sanitize all parameters
    param_values = {}
    for key in PARAM_KEYS:
        val = client_data.get(key, 0)
        param_values[key] = _parse_value(val)

    # Compute weighted score
    score = (
        param_values['financial'] * WEIGHTS['financial'] +
        param_values['operational'] * WEIGHTS['operational'] +
        param_values['compliance'] * WEIGHTS['compliance']
    )

    # Classify risk
    if score < 40:
        return "Low"
    elif 40 <= score < 70:
        return "Medium"
    else:
        return "High"

# --- Example usage (for demonstration, not required for test) ---
if __name__ == "__main__":
    example_client = {'financial': 67, 'operational': 67, 'compliance': 67}
    print(f"Risk for {example_client}: {categorize_client_risk(example_client)}")
```
