import logging
import threading
import time

import prometheus_client
import prometheus_client.core
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware

import sgp30


def create_app(sgp30_sampler=None):
    sgp30_sampler = sgp30_sampler or SGP30Sampler()
    logging.info("Starting the exporter...")
    app = Flask(__name__)
    metrics_collector_registry = prometheus_client.CollectorRegistry(auto_describe=True)
    metrics_collector_registry.register(SGP30Collector(sgp30_sampler))
    app.wsgi_app = DispatcherMiddleware(
        app.wsgi_app,
        {"/metrics": prometheus_client.make_wsgi_app(metrics_collector_registry)},
    )
    return app


class SGP30Sampler:
    def __init__(self):
        logging.info("Starting the sgp30 sampler...")
        self._air_quality = sgp30.SGP30Reading(0, 0)
        background_sampler = threading.Thread(
            target=self._sgp30_continuous_sampler, daemon=True
        )
        background_sampler.start()

    def _sgp30_continuous_sampler(self):
        logging.info("Initializing the sgp30 device...")
        sgp30_dev = sgp30.SGP30()
        sgp30_dev.start_measurement()
        logging.info("The sgp30 device has been initialized.")

        while True:
            logging.debug("Getting air quality values...")
            self._set_air_quality(sgp30_dev.get_air_quality())
            logging.debug("Got air quality values: %s", self._air_quality)
            time.sleep(1.0)

    def get_air_quality(self):
        return self._air_quality

    def _set_air_quality(self, sgp30_reading):
        self._air_quality = sgp30_reading


class SGP30Collector:
    def __init__(self, sgp30_sampler):
        logging.info("Creating the sgp30 collector...")
        self._sgp30_sampler = sgp30_sampler

    def collect(self):
        result = self._sgp30_sampler.get_air_quality()
        yield prometheus_client.core.GaugeMetricFamily(
            "sgp30_co2e_ppm",
            "Equivalent CO2 concentration",
            value=result.equivalent_co2,
        )
        yield prometheus_client.core.GaugeMetricFamily(
            "sgp30_tvoc_ppb",
            "Total volatile organic compounds concentration",
            value=result.total_voc,
        )
