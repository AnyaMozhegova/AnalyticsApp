import json
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from main import app
from models.customer import Customer
from models.report import Report
from models.report_column import ReportColumn
from models.role import Role
from services.user import get_current_user
from tests.conftest import clean_up_test, connect_test, create_customer_user


def create_test_report(customer: Customer, is_active: bool = True):
    columns = [ReportColumn(name="Column 1", column_data=[2.0, 1.0, 3.0, 6.0, None, None, 1.0],
                            indicator_values=[]).save()]
    return Report(user=customer, report_link="link", date_uploaded=datetime.strptime("01.01.2024", "%d.%m.%Y"),
                  columns=columns, fits_discriminant_analysis=False,
                  fits_correlation_analysis=False,
                  is_active=is_active).save()


def not_found_customer():
    customer_role = Role.objects(name="Customer").first()
    return Customer(name='customer_user', email="customer@gmail.com", password="customer_password!123",
                    role=customer_role)


@pytest.fixture(scope="function")
def client_setup():
    db_name = "test_db"
    connect_test(db_name)
    customer = create_customer_user()
    report = create_test_report(customer)
    with TestClient(app) as test_client:
        yield test_client, customer, report
    clean_up_test(db_name)


def test_get_reports_success(client_setup):
    client, user, report = client_setup
    app.dependency_overrides[get_current_user] = lambda: user
    response = client.get("/report/")
    assert response.status_code == 200
    report_response = json.loads(response.content.decode("utf-8"))
    assert len(report_response) == 1
    assert report_response[0]['_id'] == report.id


def test_get_reports_user_not_found(client_setup):
    client, _, _ = client_setup
    app.dependency_overrides[get_current_user] = not_found_customer
    response = client.get("/report/")
    assert response.status_code == 404


def test_get_report_success(client_setup):
    client, user, report = client_setup
    app.dependency_overrides[get_current_user] = lambda: user
    response = client.get(f"/report/{report.id}")
    assert response.status_code == 200
    report_response = json.loads(response.content.decode("utf-8"))
    assert report_response['_id'] == report.id


def test_get_report_not_found(client_setup):
    client, user, report = client_setup
    app.dependency_overrides[get_current_user] = lambda: user
    response = client.get(f"/report/{report.id + 1000}")
    assert response.status_code == 404


def test_delete_report_success(client_setup):
    client, user, report = client_setup
    app.dependency_overrides[get_current_user] = lambda: user
    response = client.delete(f"/report/{report.id}")
    assert response.status_code == 200


def test_delete_report_not_found(client_setup):
    client, user, report = client_setup
    app.dependency_overrides[get_current_user] = lambda: user
    response = client.delete(f"/report/{report.id + 1000}")
    assert response.status_code == 404
