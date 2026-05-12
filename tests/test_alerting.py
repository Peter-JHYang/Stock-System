from src.alerting import send_webhook_alert


def test_send_webhook_alert_invalid():
    # 空的 URL 或無效 URL 應回傳 False
    assert send_webhook_alert("", {"a":1}) is False
