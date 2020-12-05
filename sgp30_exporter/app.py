import logging
from typing import Generator

import prometheus_client
import prometheus_client.core
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from sgp30_exporter.sgp30_source import SGP30Source, SGP30BackgroundSamplingSource


def create_app(sgp30_source: SGP30Source = None):
    sgp30_source = sgp30_source or SGP30BackgroundSamplingSource()
    logging.info("Starting the exporter...")
    app = Flask(__name__)
    metrics_collector_registry = prometheus_client.CollectorRegistry(auto_describe=True)
    metrics_collector_registry.register(SGP30Collector(sgp30_source))
    setattr(
        app,
        "wsgi_app",
        DispatcherMiddleware(
            app.wsgi_app,
            {"/metrics": prometheus_client.make_wsgi_app(metrics_collector_registry)},
        ),
    )
    return app


class SGP30Collector:
    def __init__(self, sgp30_source: SGP30Source):
        logging.info("Creating the sgp30 collector...")
        self._sgp30_source = sgp30_source

    def collect(self) -> Generator:
        result = self._sgp30_source.get_air_quality()
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
