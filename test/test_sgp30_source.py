import logging
from unittest import mock

import backoff
import pytest
import sgp30

from sgp30_exporter import sgp30_source


def test_background_sampler(mock_sgp30_device):
    """
    check that the value read by the background sampler is propagated to the source
    """
    mock_sgp30_device.get_air_quality.return_value = sgp30.SGP30Reading(412, 123)
    sgp30_sampler = sgp30_source.SGP30BackgroundSamplingSource()
    wait_for_reading(sgp30_sampler, 412, 123)
    sgp30_source.create_sgp30_device.assert_called_once()


def test_retry_on_remote_io_failure(mock_sgp30_device, caplog):
    """
    check that the background sampler resets the device and restarts the reading
    process when an remote I/O error occurs
    """
    caplog.set_level(logging.DEBUG)
    mock_sgp30_device.get_air_quality.side_effect = OSError
    sgp30_sampler = sgp30_source.SGP30BackgroundSamplingSource(
        sample_delay_seconds=0.01
    )

    @backoff.on_exception(lambda: backoff.expo(factor=0.01), AssertionError, max_time=1)
    def _wait_for_first_call():
        assert mock_sgp30_device.get_air_quality.call_count >= 1

    _wait_for_first_call()
    assert sgp30_sampler.get_air_quality().equivalent_co2 == 0
    assert sgp30_sampler.get_air_quality().total_voc == 0

    mock_sgp30_device.get_air_quality.side_effect = lambda: sgp30.SGP30Reading(412, 123)
    wait_for_reading(sgp30_sampler, 412, 123)


@backoff.on_exception(lambda: backoff.expo(factor=0.01), AssertionError, max_time=3)
def wait_for_reading(sgp30_sampler, expected_equivalent_co2, expected_total_voc):
    assert sgp30_sampler.get_air_quality().equivalent_co2 == expected_equivalent_co2
    assert sgp30_sampler.get_air_quality().total_voc == expected_total_voc


@pytest.fixture(name="mock_sgp30_device")
def _mock_sgp30_device():
    with mock.patch(
        "sgp30_exporter.sgp30_source.create_sgp30_device"
    ) as mock_create_sgp30_device:
        mock_sgp30_device = mock.Mock()
        mock_create_sgp30_device.return_value = mock_sgp30_device
        yield mock_sgp30_device
