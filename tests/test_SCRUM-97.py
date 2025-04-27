import pytest

class ClientRiskProfiler:
    def __init__(self):
        pass
    def categorize(self, financial_score, operational_score, compliance_score):
        if not (isinstance(financial_score, (int, float)) and isinstance(operational_score, (int, float)) and isinstance(compliance_score, (int, float))):
            raise ValueError('Scores must be numeric')
        if not (0 <= financial_score <= 100 and 0 <= operational_score <= 100 and 0 <= compliance_score <= 100):
            raise ValueError('Scores must be between 0 and 100')
        avg_score = (financial_score + operational_score + compliance_score) / 3
        if avg_score >= 80:
            return 'Low'
        elif avg_score >= 50:
            return 'Medium'
        else:
            return 'High'

@pytest.fixture
def profiler():
    return ClientRiskProfiler()

def test_categorize_low_risk(profiler):
    result = profiler.categorize(90, 85, 80)
    assert result == 'Low'

def test_categorize_medium_risk(profiler):
    result = profiler.categorize(60, 55, 70)
    assert result == 'Medium'

def test_categorize_high_risk(profiler):
    result = profiler.categorize(40, 45, 35)
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

def test_categorize_invalid_scores_type(profiler):
    with pytest.raises(ValueError):
        profiler.categorize('a', 50, 60)
    with pytest.raises(ValueError):
        profiler.categorize(50, None, 60)
    with pytest.raises(ValueError):
        profiler.categorize(50, 60, [70])

def test_categorize_invalid_scores_range(profiler):
    with pytest.raises(ValueError):
        profiler.categorize(-1, 50, 60)
    with pytest.raises(ValueError):
        profiler.categorize(50, 101, 60)
    with pytest.raises(ValueError):
        profiler.categorize(50, 60, 200)

def test_categorize_all_zero_scores(profiler):
    result = profiler.categorize(0, 0, 0)
    assert result == 'High'

def test_categorize_all_max_scores(profiler):
    result = profiler.categorize(100, 100, 100)
    assert result == 'Low'

def test_categorize_mixed_scores(profiler):
    result = profiler.categorize(100, 0, 100)
    assert result == 'Medium'
    result = profiler.categorize(0, 100, 0)
    assert result == 'Medium'