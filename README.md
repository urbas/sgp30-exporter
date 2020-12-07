# sgp30-exporter [![build-badge]](https://travis-ci.com/github/urbas/sgp30-exporter) [![pypi-badge]](https://pypi.org/project/sgp30-exporter/)

Exports air quality readings from Pimoroni SGP30 to Prometheus.

This exporter uses [pimoroni-sgp30] to obtain data.

## Installation

```bash
pip install sgp30-exporter
```

## Running

```bash
sudo sgp30-exporter
```

This will serve metrics at `http://0.0.0.0:9895/metrics`.

Note that `sudo` is required to give SGP30 read-write access to the `/dev/i2c` interface.

You can make Prometheus scrape these with this scrape config:

```yaml
scrape_configs:
  - job_name: "sgp30"
    static_configs:
      - targets: ["<the IP of your exporter host>:9895"]
        labels:
          location: "bedroom"
```

[build-badge]: https://travis-ci.com/urbas/sgp30-exporter.svg?branch=master
[pimoroni-sgp30]: https://github.com/pimoroni/sgp30-python
[pypi-badge]: https://badge.fury.io/py/sgp30-exporter.svg
