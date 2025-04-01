class EmptyValueException(Exception):
    def __init__(self, datapointid):
        self.message = f"Empty value is not allowed {{datapointid={datapointid}}}"
        super().__init__(self.message)
