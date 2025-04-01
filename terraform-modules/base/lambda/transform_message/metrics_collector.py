import re


class MetricsCollector:

    def __init__(self, cloudwatch, company_namespace):
        self.metrics = {"clients": {}, "factories": {}}
        self.client_factory_mapping = {}
        self.cloudwatch = cloudwatch
        self.company_namespace = company_namespace

    def __parse_factory_from_clientid(self, client_id):
        if client_id is None:
            return None
        cached_factory = self.client_factory_mapping.get(client_id)
        if cached_factory is not None:
            return cached_factory

        match = re.search(f"^(dev_|test_|prod_){self.company_namespace}_(?P<factory>.+)_(0*\\d+)$",
                          client_id)  # with legacy format handling
        if match is not None:
            factory = match.group("factory")
            self.client_factory_mapping[client_id] = factory
            return factory
        else:
            print(f"Could not match factory for metrics: client={client_id}, make sure client name follows naming "
                  f"pattern env_clientName(without _ in it)_clientNumber")
            return None

    def send_factory_metrics(self):
        factory_metrics = self.metrics['factories']
        metrics = []
        for factory, messages_count in factory_metrics.items():
            metrics.append({
                'MetricName': 'Messages.Incoming',
                'Dimensions': [
                    {
                        'Name': 'Factory',
                        'Value': factory
                    }
                ],
                'Unit': 'None',
                'Value': messages_count
            })
        if metrics:
            response = self.cloudwatch.put_metric_data(
                MetricData=metrics,
                Namespace='IoTCoreCustom'
            )

    def send_client_metrics(self):
        client_metrics = self.metrics['clients']
        chunked_keys = self.divide_chunks(list(client_metrics.keys()))

        for group in chunked_keys:
            metrics = []
            for key in group:
                metrics.append({
                    'MetricName': 'Messages.Incoming',
                    'Dimensions': [
                        {
                            'Name': 'ClientId',
                            'Value': key
                        }
                    ],
                    'Unit': 'None',
                    'Value': client_metrics[key]
                })
            response = self.cloudwatch.put_metric_data(
                MetricData=metrics,
                Namespace='IoTCoreCustom'
            )

    def collect_metrics(self, clientid, factory_id=None):
        client_metrics = self.metrics["clients"]
        factory_metrics = self.metrics["factories"]

        if clientid is not None:
            if clientid in client_metrics:
                client_metrics[clientid] += 1
            else:
                client_metrics[clientid] = 1

        factory = factory_id or self.__parse_factory_from_clientid(clientid)
        if factory is None:
            return

        if factory in factory_metrics:
            factory_metrics[factory] += 1
        else:
            factory_metrics[factory] = 1

    def divide_chunks(self, l, chunk_size=20):
        # looping till length l
        for i in range(0, len(l), chunk_size):
            yield l[i:i + chunk_size]

