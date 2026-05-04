from __future__ import annotations

from unittest.mock import MagicMock, patch

from python_sv.notifications import notify_signup


def test_notify_signup_skips_when_no_api_key():
    with patch("python_sv.notifications.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(resend_api_key="", notification_to="")
        notify_signup("Ana", "ana@example.com", "San Salvador", "student", "backend")


def test_notify_signup_sends_email():
    with (
        patch("python_sv.notifications.get_settings") as mock_settings,
        patch("python_sv.notifications.resend") as mock_resend,
    ):
        mock_settings.return_value = MagicMock(
            resend_api_key="re_test_123",
            notification_to="admin@example.com",
            notification_from="Python SV <noreply@example.com>",
        )
        notify_signup("Ana", "ana@example.com", "San Salvador", "student", "backend")

        mock_resend.Emails.send.assert_called_once()
        call_args = mock_resend.Emails.send.call_args[0][0]
        assert call_args["to"] == ["admin@example.com"]
        assert "Ana" in call_args["subject"]


def test_notify_signup_logs_on_failure():
    with (
        patch("python_sv.notifications.get_settings") as mock_settings,
        patch("python_sv.notifications.resend") as mock_resend,
        patch("python_sv.notifications.logger") as mock_logger,
    ):
        mock_settings.return_value = MagicMock(
            resend_api_key="re_test_123",
            notification_to="admin@example.com",
            notification_from="Python SV <noreply@example.com>",
        )
        mock_resend.Emails.send.side_effect = RuntimeError("API down")
        notify_signup("Ana", "ana@example.com", "San Salvador", "student", "backend")

    mock_logger.exception.assert_called_once()
