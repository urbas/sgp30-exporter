from unittest import mock

import sgp30

from sgp30_exporter import app


def test_metrics(monkeypatch):
    """metrics endpoint produces the expected metrics"""
    mock_sgp30_sampler = mock.Mock()
    mock_sgp30_sampler.get_air_quality.return_value = sgp30.SGP30Reading(412, 123)
    response = app.create_app(mock_sgp30_sampler).test_client().get("/metrics")
    assert b"sgp30_co2e_ppm 412.0\n" in response.data
    assert b"sgp30_tvoc_ppb 123.0\n" in response.data
    assert b"Equivalent CO2" in response.data
