import main


def test_build_connection_failure_result():

    device = {
        "name": "router-02",
        "host": "192.168.77.3",
    }

    error = Exception("SSH connection timeout")

    result = main.build_connection_failure_result(
        device,
        error
    )

    assert result["device_name"] == "router-02"
    assert result["host"] == "192.168.77.3"
    assert result["status"] == "unreachable"

    assert result["data"] == {}

    assert result["summary"]["hostname"] is None
    assert result["summary"]["interface_count"] == 0
    assert result["summary"]["route_count"] == 0

    assert len(result["errors"]) == 1
    assert result["errors"][0]["section"] == "connection"
    assert result["errors"][0]["error"] == "SSH connection timeout"


def test_main_continues_after_connection_failure(
    monkeypatch,
    tmp_path
):

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SSH_PASSWORD", "test-password")

    inventory_dir = tmp_path / "inventory"
    inventory_dir.mkdir()

    inventory_file = inventory_dir / "devices.yaml"

    inventory_file.write_text(
        """
devices:
  - name: router-01
    host: 192.168.77.2
    device_type: cisco_ios
    username: admin

  - name: router-02
    host: 192.168.77.3
    device_type: cisco_ios
    username: admin
""",
        encoding="utf-8"
    )

    class FakeConnection:

        def __init__(self):
            self.disconnected = False

        def disconnect(self):
            self.disconnected = True

    fake_connection = FakeConnection()

    connection_attempts = []

    def fake_connect(device):

        connection_attempts.append(device["name"])

        if device["name"] == "router-01":
            raise Exception("SSH timeout")

        return fake_connection

    def fake_collect(connection, device):

        return {
            "device_name": device["name"],
            "host": device["host"],
            "status": "success",
            "data": {},
            "errors": [],
            "summary": {},
        }

    exported_devices = {}

    def fake_export_json(data, filename):
        exported_devices["json"] = data

    def fake_export_csv(data):
        exported_devices["csv"] = data

    monkeypatch.setattr(main, "connect_to_device", fake_connect)
    monkeypatch.setattr(main, "collect_device_data", fake_collect)
    monkeypatch.setattr(main, "export_json", fake_export_json)
    monkeypatch.setattr(main, "export_csv", fake_export_csv)

    main.main()

    results = exported_devices["json"]

    assert len(results) == 2

    assert results[0]["device_name"] == "router-01"
    assert results[0]["status"] == "unreachable"

    assert results[1]["device_name"] == "router-02"
    assert results[1]["status"] == "success"

    assert connection_attempts == ["router-01", "router-02"]

    assert fake_connection.disconnected is True

    assert exported_devices["csv"] == results
