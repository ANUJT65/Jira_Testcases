import pytest

class RiskScoringModule:
    def __init__(self, parameters):
        self.parameters = parameters
    def score_client(self, client_data):
        if not isinstance(client_data, dict):
            raise TypeError('Client data must be a dictionary')
        score = 0
        for key, weight in self.parameters.items():
            if key not in client_data:
                raise ValueError(f'Missing required data: {key}')
            value = client_data[key]
            if not isinstance(value, (int, float)):
                raise ValueError(f'Invalid data type for {key}')
            score += value * weight
        if score < 30:
            return 'Low'
        elif score < 70:
            return 'Medium'
        else:
            return 'High'

@pytest.fixture(scope='function')
def risk_module():
    parameters = {
        'financial_score': 0.5,
        'operational_score': 0.3,
        'compliance_score': 0.2
    }
    module = RiskScoringModule(parameters)
    yield module

def test_low_risk_classification(risk_module):
    client_data = {
        'financial_score': 10,
        'operational_score': 10,
        'compliance_score': 10
    }
    result = risk_module.score_client(client_data)
    assert result == 'Low'

def test_medium_risk_classification(risk_module):
    client_data = {
        'financial_score': 50,
        'operational_score': 30,
        'compliance_score': 20
    }
    result = risk_module.score_client(client_data)
    assert result == 'Medium'

def test_high_risk_classification(risk_module):
    client_data = {
        'financial_score': 100,
        'operational_score': 80,
        'compliance_score': 60
    }
    result = risk_module.score_client(client_data)
    assert result == 'High'

def test_missing_financial_score(risk_module):
    client_data = {
        'operational_score': 10,
        'compliance_score': 10
    }
    with pytest.raises(ValueError) as exc:
        risk_module.score_client(client_data)
    assert 'Missing required data: financial_score' in str(exc.value)

def test_invalid_data_type(risk_module):
    client_data = {
        'financial_score': 'ten',
        'operational_score': 10,
        'compliance_score': 10
    }
    with pytest.raises(ValueError) as exc:
        risk_module.score_client(client_data)
    assert 'Invalid data type for financial_score' in str(exc.value)

def test_negative_scores(risk_module):
    client_data = {
        'financial_score': -10,
        'operational_score': -10,
        'compliance_score': -10
    }
    result = risk_module.score_client(client_data)
    assert result == 'Low'

def test_extreme_high_scores(risk_module):
    client_data = {
        'financial_score': 1000,
        'operational_score': 1000,
        'compliance_score': 1000
    }
    result = risk_module.score_client(client_data)
    assert result == 'High'

def test_non_dict_input(risk_module):
    client_data = ['financial_score', 10, 'operational_score', 10, 'compliance_score', 10]
    with pytest.raises(TypeError) as exc:
        risk_module.score_client(client_data)
    assert 'Client data must be a dictionary' in str(exc.value)

def test_zero_scores(risk_module):
    client_data = {
        'financial_score': 0,
        'operational_score': 0,
        'compliance_score': 0
    }
    result = risk_module.score_client(client_data)
    assert result == 'Low'