import logging
import os
import re

logger = logging.getLogger("MetricsCollector")
logging.basicConfig()
logger.setLevel(logging.DEBUG)


class MetricsCollector:

    def __init__(self, cloudwatch, company_namespace):
        self.metrics = {"clients": {}, "factories": {}}
        self.cloudwatch = cloudwatch
        self.company_namespace = company_namespace
        self.client_factory_mapping = {}

    def send_factory_metrics(self):
        if os.environ.get("DRY_RUN") == "1":
            return
        factory_metrics = self.metrics["factories"]
        metrics = []
        for factory, messages_count in factory_metrics.items():
            metrics.append(
                {
                    "MetricName": "Messages.Incoming",
                    "Dimensions": [{"Name": "Factory", "Value": factory}],
                    "Unit": "None",
                    "Value": messages_count,
                }
            )
        if metrics:
            self.cloudwatch.put_metric_data(
                MetricData=metrics, Namespace="IoTCoreCustom"
            )

    def send_client_metrics(self):
        if os.environ.get("DRY_RUN") == "1":
            return
        client_metrics = self.metrics["clients"]
        chunked_keys = self.__divide_chunks(list(client_metrics.keys()))

        for group in chunked_keys:
            metrics = []
            for key in group:
                metrics.append(
                    {
                        "MetricName": "Messages.Incoming",
                        "Dimensions": [{"Name": "ClientId", "Value": key}],
                        "Unit": "None",
                        "Value": client_metrics[key],
                    }
                )
            self.cloudwatch.put_metric_data(
                MetricData=metrics, Namespace="IoTCoreCustom"
            )

    def collect_metrics(self, clientid, factory_id=None):
        client_metrics = self.metrics["clients"]
        factory_metrics = self.metrics["factories"]

        if clientid is not None:
            if clientid in client_metrics:
                client_metrics[clientid] += 1
            else:
                client_metrics[clientid] = 1

        factory = factory_id or self.__parse_factory_from_client_id(
            clientid, self.company_namespace
        )
        if factory is None:
            return

        if factory in factory_metrics:
            factory_metrics[factory] += 1
        else:
            factory_metrics[factory] = 1

    def __parse_factory_from_client_id(self, client_id, company_namespace):
        if client_id is None:
            return None
        cached_factory = self.client_factory_mapping.get(client_id)
        if cached_factory is not None:
            return cached_factory

        match = re.search(
            f"^(dev_|test_|prod_){company_namespace}_(?P<factory>.+)_(0*\\d+|debug)$",
            client_id,
        )  # with legacy format handling
        if match is not None:
            factory = match.group("factory")
            self.client_factory_mapping[client_id] = factory
            return factory
        else:
            logger.error(
                f"Could not match factory for metrics: client={client_id}, make sure client name follows naming "
                f"pattern env_clientName(without _ in it)_clientNumber"
            )
            return None

    @classmethod
    def __divide_chunks(cls, l, chunk_size=20):
        # looping till length l
        for i in range(0, len(l), chunk_size):
            yield l[i : i + chunk_size]
