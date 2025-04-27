```python
"""
client_risk_profiler.py

This module provides the ClientRiskProfiler class, which categorizes clients into
risk levels ('Low', 'Medium', 'High') based on their financial, operational, and
compliance scores. The scores must be numeric values between 0 and 100, inclusive.

The main method, `categorize`, validates input, computes the average score,
and returns the appropriate risk level according to specified thresholds.

Designed to be robust and clear, with comprehensive error handling for invalid types,
out-of-range values, and missing arguments.
"""

from typing import Union, List

class ClientRiskProfiler:
    """
    Class to profile client risk based on three numeric scores.

    Attributes:
        risk_levels (List[str]): List of possible risk levels.
    """

    def __init__(self) -> None:
        """
        Initialize the ClientRiskProfiler with predefined risk levels.
        """
        self.risk_levels: List[str] = ['Low', 'Medium', 'High']

    def categorize(
        self,
        financial_score: Union[int, float],
        operational_score: Union[int, float],
        compliance_score: Union[int, float]
    ) -> str:
        """
        Categorize the risk level based on the average of three scores.

        Args:
            financial_score (int|float): Financial score (0 to 100).
            operational_score (int|float): Operational score (0 to 100).
            compliance_score (int|float): Compliance score (0 to 100).

        Returns:
            str: Risk level ('Low', 'Medium', 'High').

        Raises:
            ValueError: If any score is not numeric.
            ValueError: If any score is outside the 0-100 range.
        """
        scores = [financial_score, operational_score, compliance_score]
        
        # Check all values are numeric (int or float)
        if not all(isinstance(score, (int, float)) for score in scores):
            raise ValueError('All scores must be numeric')

        # Check all values are within the allowed range
        if not all(0 <= score <= 100 for score in scores):
            raise ValueError('Scores must be between 0 and 100')

        avg_score = sum(scores) / 3

        # Determine risk category based on average score
        if avg_score >= 80:
            return 'Low'
        elif avg_score >= 50:
            return 'Medium'
        else:
            return 'High'
```
