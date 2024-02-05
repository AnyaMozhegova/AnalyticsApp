from schemas.report import ReportCreate


def test_report_create_success():
    report_data = {
        "user": 0,
    }
    report = ReportCreate(**report_data)
    assert report.user == report_data["user"]

