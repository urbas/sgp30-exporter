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
    wait_for_reading(get_test_sampler(), 412, 123)
    sgp30_source.create_sgp30_device.assert_called_once()


def test_retry_on_measurement_error(mock_sgp30_device):
    """
    check that the background sampler resets the device and restarts the reading
    process when an remote I/O error occurs
    """
    mock_sgp30_device.get_air_quality.side_effect = OSError
    test_sampler = get_test_sampler()

    wait_for(lambda: mock_sgp30_device.get_air_quality.call_count >= 1)
    wait_for_reading(test_sampler, 0, 0)

    mock_sgp30_device.get_air_quality.side_effect = lambda: sgp30.SGP30Reading(412, 123)
    wait_for_reading(test_sampler, 412, 123)
    assert sgp30_source.create_sgp30_device.call_count > 1


def test_retry_on_reinit_error(mock_sgp30_device):
    """
    check that the background sampler resets the device and restarts the reading
    process when an remote I/O error occurs
    """
    mock_sgp30_device.get_air_quality.side_effect = OSError
    sgp30_sampler = sgp30_source.BackgroundSampler(sample_delay_seconds=0.01)

    wait_for(lambda: mock_sgp30_device.get_air_quality.call_count >= 1)
    wait_for_reading(sgp30_sampler, 0, 0)

    # Here we simulate a temporary error during the device initialization process
    sgp30_source.create_sgp30_device.side_effect = OSError
    call_count_before = sgp30_source.create_sgp30_device.call_count
    wait_for(lambda: sgp30_source.create_sgp30_device.call_count > call_count_before)

    # Now stop producing errors and behave nicely:
    sgp30_source.create_sgp30_device.side_effect = lambda: mock_sgp30_device
    mock_sgp30_device.get_air_quality.side_effect = lambda: sgp30.SGP30Reading(412, 123)

    # Now that everything is back in order, we should start seeing measurements again
    wait_for_reading(sgp30_sampler, 412, 123)
    assert sgp30_source.create_sgp30_device.call_count > 1


@backoff.on_exception(lambda: backoff.expo(factor=0.01), AssertionError, max_time=3)
def wait_for(predicate):
    assert predicate()


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


def get_test_sampler():
    return sgp30_source.BackgroundSampler(sample_delay_seconds=0.01)
