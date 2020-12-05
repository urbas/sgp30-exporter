import abc
import logging
import threading
import time

import sgp30


class SGP30Source(abc.ABC):
    @abc.abstractmethod
    def get_air_quality(self) -> sgp30.SGP30Reading:
        ...  # pragma: no cover


class SGP30BackgroundSamplingSource(SGP30Source):
    def __init__(self, sample_delay_seconds=1):
        logging.info("Starting the sgp30 sampler...")
        self._air_quality = sgp30.SGP30Reading(0, 0)
        self._sample_delay_seconds = sample_delay_seconds
        background_sampler_thread = threading.Thread(
            target=self._sgp30_continuous_sampler, daemon=True
        )
        background_sampler_thread.start()

    def _sgp30_continuous_sampler(self):
        # NB: every now and then communications with the SGP30 device can break down.
        # An OSError number 121 (Remote I/O error) is thrown in this case. The only
        # option in this case is to reset the SGP30 device and restart communications.
        sgp30_dev = create_sgp30_device()

        while True:
            logging.debug("Getting air quality values...")
            try:
                self._set_air_quality(sgp30_dev.get_air_quality())
                logging.debug("Got air quality values: %s", self._air_quality)
                time.sleep(self._sample_delay_seconds)
            except OSError as ex:
                time.sleep(self._sample_delay_seconds)
                logging.error(
                    "Failed to communicate with the SGP30 device. Internal error: %s. "
                    "Trying to reconnect...",
                    ex,
                )
                sgp30_dev = create_sgp30_device()

    def get_air_quality(self):
        return self._air_quality

    def _set_air_quality(self, sgp30_reading):
        self._air_quality = sgp30_reading


def create_sgp30_device():  # pragma: no cover
    logging.info("Initializing the sgp30 device...")
    sgp30_dev = sgp30.SGP30()
    sgp30_dev.start_measurement()
    logging.info("The sgp30 device has been initialized.")
    return sgp30_dev
