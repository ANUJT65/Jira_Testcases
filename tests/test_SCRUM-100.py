import pytest
import logging
from unittest import mock

class MockCloudWatchClient:
    def __init__(self):
        self.metrics = []
        self.alarms = []
        self.put_metric_data_called = False
        self.put_metric_alarm_called = False
    def put_metric_data(self, Namespace, MetricData):
        self.put_metric_data_called = True
        self.metrics.append((Namespace, MetricData))
        return {'ResponseMetadata': {'HTTPStatusCode': 200}}
    def put_metric_alarm(self, **kwargs):
        self.put_metric_alarm_called = True
        self.alarms.append(kwargs)
        return {'ResponseMetadata': {'HTTPStatusCode': 200}}
    def get_metric_data(self, MetricDataQueries):
        return {'MetricDataResults': [{'Id': 'm1', 'Values': [1]}]}
    def describe_alarms(self, AlarmNames):
        return {'MetricAlarms': [{'AlarmName': name, 'StateValue': 'ALARM'} for name in AlarmNames]}

@pytest.fixture(scope="function")
def setup_audit_log(tmp_path):
    log_file = tmp_path / "audit.log"
    logger = logging.getLogger("audit")
    handler = logging.FileHandler(log_file)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    yield logger, log_file
    logger.removeHandler(handler)
    handler.close()

@pytest.fixture(scope="function")
def mock_cloudwatch_client():
    client = MockCloudWatchClient()
    yield client

# Positive Test: Audit logs are written and maintained
def test_audit_log_written_and_maintained(setup_audit_log):
    logger, log_file = setup_audit_log
    logger.info("User X performed action Y")
    logger.info("User Z performed action W")
    with open(log_file, 'r') as f:
        contents = f.read()
    assert "User X performed action Y" in contents
    assert "User Z performed action W" in contents
    assert len(contents.splitlines()) == 2

# Negative Test: Audit log is not writable
def test_audit_log_not_writable(tmp_path):
    log_file = tmp_path / "audit.log"
    log_file.write_text("")
    log_file.chmod(0o400)
    logger = logging.getLogger("audit_fail")
    handler = logging.FileHandler(log_file)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    with pytest.raises(PermissionError):
        logger.info("Should fail to write")
    logger.removeHandler(handler)
    handler.close()

# Positive Test: CloudWatch metric data is sent successfully
def test_cloudwatch_metric_data_sent(mock_cloudwatch_client):
    client = mock_cloudwatch_client
    response = client.put_metric_data(Namespace="MyApp", MetricData=[{"MetricName": "Errors", "Value": 1}])
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200
    assert client.put_metric_data_called
    assert client.metrics[0][0] == "MyApp"
    assert client.metrics[0][1][0]["MetricName"] == "Errors"

# Negative Test: CloudWatch metric data fails to send
def test_cloudwatch_metric_data_send_failure(monkeypatch, mock_cloudwatch_client):
    client = mock_cloudwatch_client
    def fail_put_metric_data(Namespace, MetricData):
        raise Exception("AWS CloudWatch unavailable")
    monkeypatch.setattr(client, "put_metric_data", fail_put_metric_data)
    with pytest.raises(Exception) as exc:
        client.put_metric_data(Namespace="MyApp", MetricData=[{"MetricName": "Errors", "Value": 1}])
    assert "unavailable" in str(exc.value)

# Positive Test: CloudWatch alarm is created and triggers alert
def test_cloudwatch_alarm_created_and_alerted(mock_cloudwatch_client):
    client = mock_cloudwatch_client
    alarm_name = "HighErrorRate"
    response = client.put_metric_alarm(AlarmName=alarm_name, MetricName="Errors", Threshold=5, ComparisonOperator="GreaterThanThreshold")
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200
    assert client.put_metric_alarm_called
    alarms = client.describe_alarms(AlarmNames=[alarm_name])
    assert alarms['MetricAlarms'][0]['AlarmName'] == alarm_name
    assert alarms['MetricAlarms'][0]['StateValue'] == 'ALARM'

# Negative Test: CloudWatch alarm creation fails
def test_cloudwatch_alarm_creation_failure(monkeypatch, mock_cloudwatch_client):
    client = mock_cloudwatch_client
    def fail_put_metric_alarm(**kwargs):
        raise Exception("Alarm creation failed")
    monkeypatch.setattr(client, "put_metric_alarm", fail_put_metric_alarm)
    with pytest.raises(Exception) as exc:
        client.put_metric_alarm(AlarmName="FailAlarm", MetricName="Errors", Threshold=5, ComparisonOperator="GreaterThanThreshold")
    assert "Alarm creation failed" in str(exc.value)

# Positive Test: Audit log contains required information
def test_audit_log_contains_required_info(setup_audit_log):
    logger, log_file = setup_audit_log
    logger.info("User:admin Action:restart_service Status:success")
    with open(log_file, 'r') as f:
        contents = f.read()
    assert "User:admin" in contents
    assert "Action:restart_service" in contents
    assert "Status:success" in contents

# Negative Test: Audit log missing required information
def test_audit_log_missing_required_info(setup_audit_log):
    logger, log_file = setup_audit_log
    logger.info("Action:restart_service Status:success")
    with open(log_file, 'r') as f:
        contents = f.read()
    assert "User:" not in contents

# Positive Test: CloudWatch monitoring provides continuous data
def test_cloudwatch_monitoring_continuous_data(mock_cloudwatch_client):
    client = mock_cloudwatch_client
    data = client.get_metric_data(MetricDataQueries=[{"Id": "m1", "MetricStat": {}}])
    assert 'MetricDataResults' in data
    assert data['MetricDataResults'][0]['Values'] == [1]

# Negative Test: CloudWatch monitoring data unavailable
def test_cloudwatch_monitoring_data_unavailable(monkeypatch, mock_cloudwatch_client):
    client = mock_cloudwatch_client
    def fail_get_metric_data(MetricDataQueries):
        raise Exception("Data unavailable")
    monkeypatch.setattr(client, "get_metric_data", fail_get_metric_data)
    with pytest.raises(Exception) as exc:
        client.get_metric_data(MetricDataQueries=[{"Id": "m1", "MetricStat": {}}])
    assert "Data unavailable" in str(exc.value)