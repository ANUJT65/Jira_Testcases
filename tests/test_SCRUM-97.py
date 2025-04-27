import pytest

class ClientRiskProfiler:
    def __init__(self):
        self.risk_levels = ['Low', 'Medium', 'High']

    def categorize(self, financial_score, operational_score, compliance_score):
        if not all(isinstance(score, (int, float)) for score in [financial_score, operational_score, compliance_score]):
            raise ValueError('All scores must be numeric')
        if not all(0 <= score <= 100 for score in [financial_score, operational_score, compliance_score]):
            raise ValueError('Scores must be between 0 and 100')
        avg_score = (financial_score + operational_score + compliance_score) / 3
        if avg_score >= 80:
            return 'Low'
        elif avg_score >= 50:
            return 'Medium'
        else:
            return 'High'

@pytest.fixture(scope='function')
def profiler():
    profiler = ClientRiskProfiler()
    yield profiler
    del profiler

def test_categorize_low_risk(profiler):
    result = profiler.categorize(90, 85, 80)
    assert result == 'Low'

def test_categorize_medium_risk(profiler):
    result = profiler.categorize(60, 55, 65)
    assert result == 'Medium'

def test_categorize_high_risk(profiler):
    result = profiler.categorize(30, 40, 45)
    assert result == 'High'

def test_categorize_boundary_low_medium(profiler):
    result = profiler.categorize(80, 80, 80)
    assert result == 'Low'
    result = profiler.categorize(79.9, 79.9, 79.9)
    assert result == 'Medium'

def test_categorize_boundary_medium_high(profiler):
    result = profiler.categorize(50, 50, 50)
    assert result == 'Medium'
    result = profiler.categorize(49.9, 49.9, 49.9)
    assert result == 'High'

def test_invalid_score_type(profiler):
    with pytest.raises(ValueError) as excinfo:
        profiler.categorize('a', 50, 60)
    assert 'numeric' in str(excinfo.value)

def test_score_below_zero(profiler):
    with pytest.raises(ValueError) as excinfo:
        profiler.categorize(-1, 50, 60)
    assert 'between 0 and 100' in str(excinfo.value)

def test_score_above_hundred(profiler):
    with pytest.raises(ValueError) as excinfo:
        profiler.categorize(101, 50, 60)
    assert 'between 0 and 100' in str(excinfo.value)

def test_missing_scores(profiler):
    with pytest.raises(TypeError):
        profiler.categorize(50, 60)

def test_extreme_valid_scores(profiler):
    result = profiler.categorize(0, 0, 0)
    assert result == 'High'
    result = profiler.categorize(100, 100, 100)
    assert result == 'Low'