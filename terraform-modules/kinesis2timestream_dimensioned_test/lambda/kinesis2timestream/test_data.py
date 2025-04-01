from unittest.mock import call

event_empty = {
    "Records": [
        {
            #  just an empty dict: {}
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "78b1ffdf-f89d-4193-9739-fcb4aee171f8",
                "sequenceNumber": "49628516550903612936269980587023092715698276672229867522",
                "data": "e30=",
                "approximateArrivalTimestamp": 1649781721.789,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49628516550903612936269980587023092715698276672229867522",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::093961187306:role/dev_plcf_glinojeckSFC_kinesis2timestream_lambda",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_glinojeckSFC_timeseries_data_stream",
        },
        {
            #  {"value":100}
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "e07294a8-ccef-4998-88d8-49c59d4e2efd",
                "sequenceNumber": "49628516550903612936269980587024301641517891370124050434",
                "data": "eyJ2YWx1ZSI6MTAwfQ==",
                "approximateArrivalTimestamp": 1649781723.284,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49628516550903612936269980587024301641517891370124050434",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::093961187306:role/dev_plcf_glinojeckSFC_kinesis2timestream_lambda",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_glinojeckSFC_timeseries_data_stream",
        },
        {
            # value = "" empty string
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "e07294a8-ccef-4998-88d8-49c59d4e2ef5",
                "sequenceNumber": "49628516550903612936269980587024301641517891370124050435",
                "data": "eyJkYXRhIjp7ImRhdGFQb2ludElkIjoiVEVTVF9SV19PUENfU1RSIiwidmFsdWUiOiIiLCJ0YWtlbkF0IjoiMjAyMi0wNC0xMlQxNjo1Mzo1MC45MDRaIiwicG9zdGVkQXQiOiIyMDIyLTA0LTEyVDE2OjUzOjUzLjgwNloiLCJtb2RlbFZlcnNpb24iOiIwLjEuMCIsImNvbmZpZ3VyYXRpb25Nb2RlbFZlcnNpb24iOiIwLjEuMCIsInRpbWVzdHJlYW0iOnRydWV9LCJjbGllbnRpZCI6ImRldl9wbGNmX2dsaW5vamVja1NGQ18wMDAxIn0=",
                "approximateArrivalTimestamp": 1649781723.284,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49628516550903612936269980587024301641517891370124050434",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::093961187306:role/dev_plcf_glinojeckSFC_kinesis2timestream_lambda",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_glinojeckSFC_timeseries_data_stream",
        },
    ]
}
event_value_string_to_long = {
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "6000fc03-2b97-40c3-b3ad-6cbbad51e26b",
                "sequenceNumber": "49628516550903612936269980587021883789878662043055161346",
                "data": "eyJkYXRhIjpbeyAiZGF0YVBvaW50SWQiOiAidGVzdF9KU19UX09FMV9DSEFOTkVMMV9XYXZlbGVuZ3RoIiwgInZhbHVlIjogWzEsIDk1MCwgOTUxLCA5NTIsIDk1MywgOTU0LCA5NTUsIDk1NiwgOTU3LCA5NTgsIDk1OSwgOTYwLCA5NjEsIDk2MiwgOTYzLCA5NjQsIDk2NSwgOTY2LCA5NjcsIDk2OCwgOTY5LCA5NzAsIDk3MSwgOTcyLCA5NzMsIDk3NCwgOTc1LCA5NzYsIDk3NywgOTc4LCA5NzksIDk4MCwgOTgxLCA5ODIsIDk4MywgOTg0LCA5ODUsIDk4NiwgOTg3LCA5ODgsIDk4OSwgOTkwLCA5OTEsIDk5MiwgOTkzLCA5OTQsIDk5NSwgOTk2LCA5OTcsIDk5OCwgOTk5LCAxMDAwLCAxMDAxLCAxMDAyLCAxMDAzLCAxMDA0LCAxMDA1LCAxMDA2LCAxMDA3LCAxMDA4LCAxMDA5LCAxMDEwLCAxMDExLCAxMDEyLCAxMDEzLCAxMDE0LCAxMDE1LCAxMDE2LCAxMDE3LCAxMDE4LCAxMDE5LCAxMDIwLCAxMDIxLCAxMDIyLCAxMDIzLCAxMDI0LCAxMDI1LCAxMDI2LCAxMDI3LCAxMDI4LCAxMDI5LCAxMDMwLCAxMDMxLCAxMDMyLCAxMDMzLCAxMDM0LCAxMDM1LCAxMDM2LCAxMDM3LCAxMDM4LCAxMDM5LCAxMDQwLCAxMDQxLCAxMDQyLCAxMDQzLCAxMDQ0LCAxMDQ1LCAxMDQ2LCAxMDQ3LCAxMDQ4LCAxMDQ5LCAxMDUwLCAxMDUxLCAxMDUyLCAxMDUzLCAxMDU0LCAxMDU1LCAxMDU2LCAxMDU3LCAxMDU4LCAxMDU5LCAxMDYwLCAxMDYxLCAxMDYyLCAxMDYzLCAxMDY0LCAxMDY1LCAxMDY2LCAxMDY3LCAxMDY4LCAxMDY5LCAxMDcwLCAxMDcxLCAxMDcyLCAxMDczLCAxMDc0LCAxMDc1LCAxMDc2LCAxMDc3LCAxMDc4LCAxMDc5LCAxMDgwLCAxMDgxLCAxMDgyLCAxMDgzLCAxMDg0LCAxMDg1LCAxMDg2LCAxMDg3LCAxMDg4LCAxMDg5LCAxMDkwLCAxMDkxLCAxMDkyLCAxMDkzLCAxMDk0LCAxMDk1LCAxMDk2LCAxMDk3LCAxMDk4LCAxMDk5LCAxMTAwLCAxMTAxLCAxMTAyLCAxMTAzLCAxMTA0LCAxMTA1LCAxMTA2LCAxMTA3LCAxMTA4LCAxMTA5LCAxMTEwLCAxMTExLCAxMTEyLCAxMTEzLCAxMTE0LCAxMTE1LCAxMTE2LCAxMTE3LCAxMTE4LCAxMTE5LCAxMTIwLCAxMTIxLCAxMTIyLCAxMTIzLCAxMTI0LCAxMTI1LCAxMTI2LCAxMTI3LCAxMTI4LCAxMTI5LCAxMTMwLCAxMTMxLCAxMTMyLCAxMTMzLCAxMTM0LCAxMTM1LCAxMTM2LCAxMTM3LCAxMTM4LCAxMTM5LCAxMTQwLCAxMTQxLCAxMTQyLCAxMTQzLCAxMTQ0LCAxMTQ1LCAxMTQ2LCAxMTQ3LCAxMTQ4LCAxMTQ5LCAxMTUwLCAxMTUxLCAxMTUyLCAxMTUzLCAxMTU0LCAxMTU1LCAxMTU2LCAxMTU3LCAxMTU4LCAxMTU5LCAxMTYwLCAxMTYxLCAxMTYyLCAxMTYzLCAxMTY0LCAxMTY1LCAxMTY2LCAxMTY3LCAxMTY4LCAxMTY5LCAxMTcwLCAxMTcxLCAxMTcyLCAxMTczLCAxMTc0LCAxMTc1LCAxMTc2LCAxMTc3LCAxMTc4LCAxMTc5LCAxMTgwLCAxMTgxLCAxMTgyLCAxMTgzLCAxMTg0LCAxMTg1LCAxMTg2LCAxMTg3LCAxMTg4LCAxMTg5LCAxMTkwLCAxMTkxLCAxMTkyLCAxMTkzLCAxMTk0LCAxMTk1LCAxMTk2LCAxMTk3LCAxMTk4LCAxMTk5LCAxMjAwLCAxMjAxLCAxMjAyLCAxMjAzLCAxMjA0LCAxMjA1LCAxMjA2LCAxMjA3LCAxMjA4LCAxMjA5LCAxMjEwLCAxMjExLCAxMjEyLCAxMjEzLCAxMjE0LCAxMjE1LCAxMjE2LCAxMjE3LCAxMjE4LCAxMjE5LCAxMjIwLCAxMjIxLCAxMjIyLCAxMjIzLCAxMjI0LCAxMjI1LCAxMjI2LCAxMjI3LCAxMjI4LCAxMjI5LCAxMjMwLCAxMjMxLCAxMjMyLCAxMjMzLCAxMjM0LCAxMjM1LCAxMjM2LCAxMjM3LCAxMjM4LCAxMjM5LCAxMjQwLCAxMjQxLCAxMjQyLCAxMjQzLCAxMjQ0LCAxMjQ1LCAxMjQ2LCAxMjQ3LCAxMjQ4LCAxMjQ5LCAxMjUwLCAxMjUxLCAxMjUyLCAxMjUzLCAxMjU0LCAxMjU1LCAxMjU2LCAxMjU3LCAxMjU4LCAxMjU5LCAxMjYwLCAxMjYxLCAxMjYyLCAxMjYzLCAxMjY0LCAxMjY1LCAxMjY2LCAxMjY3LCAxMjY4LCAxMjY5LCAxMjcwLCAxMjcxLCAxMjcyLCAxMjczLCAxMjc0LCAxMjc1LCAxMjc2LCAxMjc3LCAxMjc4LCAxMjc5LCAxMjgwLCAxMjgxLCAxMjgyLCAxMjgzLCAxMjg0LCAxMjg1LCAxMjg2LCAxMjg3LCAxMjg4LCAxMjg5LCAxMjkwLCAxMjkxLCAxMjkyLCAxMjkzLCAxMjk0LCAxMjk1LCAxMjk2LCAxMjk3LCAxMjk4LCAxMjk5LCAxMzAwLCAxMzAxLCAxMzAyLCAxMzAzLCAxMzA0LCAxMzA1LCAxMzA2LCAxMzA3LCAxMzA4LCAxMzA5LCAxMzEwLCAxMzExLCAxMzEyLCAxMzEzLCAxMzE0LCAxMzE1LCAxMzE2LCAxMzE3LCAxMzE4LCAxMzE5LCAxMzIwLCAxMzIxLCAxMzIyLCAxMzIzLCAxMzI0LCAxMzI1LCAxMzI2LCAxMzI3LCAxMzI4LCAxMzI5LCAxMzMwLCAxMzMxLCAxMzMyLCAxMzMzLCAxMzM0LCAxMzM1LCAxMzM2LCAxMzM3LCAxMzM4LCAxMzM5LCAxMzQwLCAxMzQxLCAxMzQyLCAxMzQzLCAxMzQ0LCAxMzQ1LCAxMzQ2LCAxMzQ3LCAxMzQ4LCAxMzQ5LCAxMzUwLCAxMzUxLCAxMzUyLCAxMzUzLCAxMzU0LCAxMzU1LCAxMzU2LCAxMzU3LCAxMzU4LCAxMzU5LCAxMzYwLCAxMzYxLCAxMzYyLCAxMzYzLCAxMzY0LCAxMzY1LCAxMzY2LCAxMzY3LCAxMzY4LCAxMzY5LCAxMzcwLCAxMzcxLCAxMzcyLCAxMzczLCAxMzc0LCAxMzc1LCAxMzc2LCAxMzc3LCAxMzc4LCAxMzc5LCAxMzgwLCAxMzgxLCAxMzgyLCAxMzgzLCAxMzg0LCAxMzg1LCAxMzg2LCAxMzg3LCAxMzg4LCAxMzg5LCAxMzkwLCAxMzkxLCAxMzkyLCAxMzkzLCAxMzk0LCAxMzk1LCAxMzk2LCAxMzk3LCAxMzk4LCAxMzk5LCAxNDAwLCAxNDAxLCAxNDAyLCAxNDAzLCAxNDA0LCAxNDA1LCAxNDA2LCAxNDA3LCAxNDA4LCAxNDA5LCAxNDEwLCAxNDExLCAxNDEyLCAxNDEzLCAxNDE0LCAxNDE1LCAxNDE2LCAxNDE3LCAxNDE4LCAxNDE5LCAxNDIwLCAxNDIxLCAxNDIyLCAxNDIzLCAxNDI0LCAxNDI1LCAxNDI2LCAxNDI3LCAxNDI4LCAxNDI5LCAxNDMwLCAxNDMxLCAxNDMyLCAxNDMzLCAxNDM0LCAxNDM1LCAxNDM2LCAxNDM3LCAxNDM4LCAxNDM5LCAxNDQwLCAxNDQxLCAxNDQyLCAxNDQzLCAxNDQ0LCAxNDQ1LCAxNDQ2LCAxNDQ3LCAxNDQ4LCAxNDQ5LCAxNDUwLCAxNDUxLCAxNDUyLCAxNDUzLCAxNDU0LCAxNDU1LCAxNDU2LCAxNDU3LCAxNDU4LCAxNDU5LCAxNDYwLCAxNDYxLCAxNDYyLCAxNDYzLCAxNDY0LCAxNDY1LCAxNDY2LCAxNDY3LCAxNDY4LCAxNDY5LCAxNDcwLCAxNDcxLCAxNDcyLCAxNDczLCAxNDc0LCAxNDc1LCAxNDc2LCAxNDc3LCAxNDc4LCAxNDc5LCAxNDgwLCAxNDgxLCAxNDgyLCAxNDgzLCAxNDg0LCAxNDg1LCAxNDg2LCAxNDg3LCAxNDg4LCAxNDg5LCAxNDkwLCAxNDkxLCAxNDkyLCAxNDkzLCAxNDk0LCAxNDk1LCAxNDk2LCAxNDk3LCAxNDk4LCAxNDk5LCAxNTAwLCAxNTAxLCAxNTAyLCAxNTAzLCAxNTA0LCAxNTA1LCAxNTA2LCAxNTA3LCAxNTA4LCAxNTA5LCAxNTEwLCAxNTExLCAxNTEyLCAxNTEzLCAxNTE0LCAxNTE1LCAxNTE2LCAxNTE3LCAxNTE4LCAxNTE5LCAxNTIwLCAxNTIxLCAxNTIyLCAxNTIzLCAxNTI0LCAxNTI1LCAxNTI2LCAxNTI3LCAxNTI4LCAxNTI5LCAxNTMwLCAxNTMxLCAxNTMyLCAxNTMzLCAxNTM0LCAxNTM1LCAxNTM2LCAxNTM3LCAxNTM4LCAxNTM5LCAxNTQwLCAxNTQxLCAxNTQyLCAxNTQzLCAxNTQ0LCAxNTQ1LCAxNTQ2LCAxNTQ3LCAxNTQ4LCAxNTQ5LCAxNTUwLCAxNTUxLCAxNTUyLCAxNTUzLCAxNTU0LCAxNTU1LCAxNTU2LCAxNTU3LCAxNTU4LCAxNTU5LCAxNTYwLCAxNTYxLCAxNTYyLCAxNTYzLCAxNTY0LCAxNTY1LCAxNTY2LCAxNTY3LCAxNTY4LCAxNTY5LCAxNTcwLCAxNTcxLCAxNTcyLCAxNTczLCAxNTc0LCAxNTc1LCAxNTc2LCAxNTc3LCAxNTc4LCAxNTc5LCAxNTgwLCAxNTgxLCAxNTgyLCAxNTgzLCAxNTg0LCAxNTg1LCAxNTg2LCAxNTg3LCAxNTg4LCAxNTg5LCAxNTkwLCAxNTkxLCAxNTkyLCAxNTkzLCAxNTk0LCAxNTk1LCAxNTk2LCAxNTk3LCAxNTk4LCAxNTk5LCAxNjAwLCAxNjAxLCAxNjAyLCAxNjAzLCAxNjA0LCAxNjA1LCAxNjA2LCAxNjA3LCAxNjA4LCAxNjA5LCAxNjEwLCAxNjExLCAxNjEyLCAxNjEzLCAxNjE0LCAxNjE1LCAxNjE2LCAxNjE3LCAxNjE4LCAxNjE5LCAxNjIwLCAxNjIxLCAxNjIyLCAxNjIzLCAxNjI0LCAxNjI1LCAxNjI2LCAxNjI3LCAxNjI4LCAxNjI5LCAxNjMwLCAxNjMxLCAxNjMyLCAxNjMzLCAxNjM0LCAxNjM1LCAxNjM2LCAxNjM3LCAxNjM4LCAxNjM5LCAxNjQwLCAxNjQxLCAxNjQyLCAxNjQzLCAxNjQ0LCAxNjQ1LCAxNjQ2LCAxNjQ3LCAxNjQ4LCAxNjQ5LCAxNjUwLCAxNjUxLCAxNjUyLCAxNjUzLCAxNjU0LCAxNjU1LCAxNjU2LCAxNjU3LCAxNjU4LCAxNjU5LCAxNjYwLCAxNjYxLCAxNjYyLCAxNjYzLCAxNjY0LCAxNjY1LCAxNjY2LCAxNjY3LCAxNjY4LCAxNjY5LCAxNjcwLCAxNjcxLCAxNjcyLCAxNjczLCAxNjc0LCAxNjc1LCAxNjc2LCAxNjc3LCAxNjc4LCAxNjc5LCAxNjgwLCAxNjgxLCAxNjgyLCAxNjgzLCAxNjg0LCAxNjg1LCAxNjg2LCAxNjg3LCAxNjg4LCAxNjg5LCAxNjkwLCAxNjkxLCAxNjkyLCAxNjkzLCAxNjk0LCAxNjk1LCAxNjk2LCAxNjk3LCAxNjk4LCAxNjk5LCAxNzAwLCAxNzAxLCAxNzAyLCAxNzAzLCAxNzA0LCAxNzA1LCAxNzA2LCAxNzA3LCAxNzA4LCAxNzA5LCAxNzEwLCAxNzExLCAxNzEyLCAxNzEzLCAxNzE0LCAxNzE1LCAxNzE2LCAxNzE3LCAxNzE4LCAxNzE5LCAxNzIwLCAxNzIxLCAxNzIyLCAxNzIzLCAxNzI0LCAxNzI1LCAxNzI2LCAxNzI3LCAxNzI4LCAxNzI5LCAxNzMwLCAxNzMxLCAxNzMyLCAxNzMzLCAxNzM0LCAxNzM1LCAxNzM2LCAxNzM3LCAxNzM4LCAxNzM5LCAxNzQwLCAxNzQxLCAxNzQyLCAxNzQzLCAxNzQ0LCAxNzQ1LCAxNzQ2LCAxNzQ3LCAxNzQ4LCAxNzQ5LCAxNzUwLCAxNzUxLCAxNzUyLCAxNzUzLCAxNzU0LCAxNzU1LCAxNzU2LCAxNzU3LCAxNzU4LCAxNzU5LCAxNzYwLCAxNzYxLCAxNzYyLCAxNzYzLCAxNzY0LCAxNzY1LCAxNzY2LCAxNzY3LCAxNzY4LCAxNzY5LCAxNzcwLCAxNzcxLCAxNzcyLCAxNzczLCAxNzc0LCAxNzc1LCAxNzc2LCAxNzc3LCAxNzc4LCAxNzc5LCAxNzgwLCAxNzgxLCAxNzgyLCAxNzgzLCAxNzg0LCAxNzg1LCAxNzg2LCAxNzg3LCAxNzg4LCAxNzg5LCAxNzkwLCAxNzkxLCAxNzkyLCAxNzkzLCAxNzk0LCAxNzk1LCAxNzk2LCAxNzk3LCAxNzk4LCAxNzk5LCAxODAwLCAxODAxLCAxODAyLCAxODAzLCAxODA0LCAxODA1LCAxODA2LCAxODA3LCAxODA4LCAxODA5LCAxODEwLCAxODExLCAxODEyLCAxODEzLCAxODE0LCAxODE1LCAxODE2LCAxODE3LCAxODE4LCAxODE5LCAxODIwLCAxODIxLCAxODIyLCAxODIzLCAxODI0LCAxODI1LCAxODI2LCAxODI3LCAxODI4LCAxODI5LCAxODMwLCAxODMxLCAxODMyLCAxODMzLCAxODM0LCAxODM1LCAxODM2LCAxODM3LCAxODM4LCAxODM5LCAxODQwLCAxODQxLCAxODQyLCAxODQzLCAxODQ0LCAxODQ1LCAxODQ2LCAxODQ3LCAxODQ4LCAxODQ5LCAxODUwLCAxODUxLCAxODUyLCAxODUzLCAxODU0LCAxODU1LCAxODU2LCAxODU3LCAxODU4LCAxODU5LCAxODYwLCAxODYxLCAxODYyLCAxODYzLCAxODY0LCAxODY1LCAxODY2LCAxODY3LCAxODY4LCAxODY5LCAxODcwLCAxODcxLCAxODcyLCAxODczLCAxODc0LCAxODc1LCAxODc2LCAxODc3LCAxODc4LCAxODc5LCAxODgwLCAxODgxLCAxODgyLCAxODgzLCAxODg0LCAxODg1LCAxODg2LCAxODg3LCAxODg4LCAxODg5LCAxODkwLCAxODkxLCAxODkyLCAxODkzLCAxODk0LCAxODk1LCAxODk2LCAxODk3LCAxODk4LCAxODk5LCAxOTAwLCAxOTAxLCAxOTAyLCAxOTAzLCAxOTA0LCAxOTA1LCAxOTA2LCAxOTA3LCAxOTA4LCAxOTA5LCAxOTEwLCAxOTExLCAxOTEyLCAxOTEzLCAxOTE0LCAxOTE1LCAxOTE2LCAxOTE3LCAxOTE4LCAxOTE5LCAxOTIwLCAxOTIxLCAxOTIyLCAxOTIzLCAxOTI0LCAxOTI1LCAxOTI2LCAxOTI3LCAxOTI4LCAxOTI5LCAxOTMwLCAxOTMxLCAxOTMyLCAxOTMzLCAxOTM0LCAxOTM1LCAxOTM2LCAxOTM3LCAxOTM4LCAxOTM5LCAxOTQwLCAxOTQxLCAxOTQyLCAxOTQzLCAxOTQ0LCAxOTQ1LCAxOTQ2LCAxOTQ3LCAxOTQ4LCAxOTQ5LCAxOTUwLCAxOTUxLCAxOTUyLCAxOTUzLCAxOTU0LCAxOTU1LCAxOTU2LCAxOTU3LCAxOTU4LCAxOTU5LCAxOTYwLCAxOTYxLCAxOTYyLCAxOTYzLCAxOTY0LCAxOTY1LCAxOTY2LCAxOTY3LCAxOTY4LCAxOTY5LCAxOTcwLCAxOTcxLCAxOTcyLCAxOTczLCAxOTc0LCAxOTc1LCAxOTc2LCAxOTc3LCAxOTc4LCAxOTc5LCAxOTgwLCAxOTgxLCAxOTgyLCAxOTgzLCAxOTg0LCAxOTg1LCAxOTg2LCAxOTg3LCAxOTg4LCAxOTg5LCAxOTkwLCAxOTkxLCAxOTkyLCAxOTkzLCAxOTk0LCAxOTk1LCAxOTk2LCAxOTk3LCAxOTk4LCAxOTk5LCAyMDAwLCAyMDAxLCAyMDAyLCAyMDAzLCAyMDA0LCAyMDA1LCAyMDA2LCAyMDA3LCAyMDA4LCAyMDA5LCAyMDEwLCAyMDExLCAyMDEyLCAyMDEzLCAyMDE0LCAyMDE1LCAyMDE2LCAyMDE3LCAyMDE4LCAyMDE5LCAyMDIwLCAyMDIxLCAyMDIyLCAyMDIzLCAyMDI0LCAyMDI1LCAyMDI2LCAyMDI3LCAyMDI4LCAyMDI5LCAyMDMwLCAyMDMxLCAyMDMyLCAyMDMzLCAyMDM0LCAyMDM1LCAyMDM2LCAyMDM3LCAyMDM4LCAyMDM5LCAyMDQwLCAyMDQxLCAyMDQyLCAyMDQzLCAyMDQ0LCAyMDQ1LCAyMDQ2LCAyMDQ3LCAyMDQ4LCAyMDQ5LCAyMDUwLCAyMDUxLCAyMDUyLCAyMDUzLCAyMDU0LCAyMDU1LCAyMDU2LCAyMDU3LCAyMDU4LCAyMDU5LCAyMDYwLCAyMDYxLCAyMDYyLCAyMDYzLCAyMDY0LCAyMDY1LCAyMDY2LCAyMDY3LCAyMDY4LCAyMDY5LCAyMDcwLCAyMDcxLCAyMDcyLCAyMDczLCAyMDc0LCAyMDc1LCAyMDc2LCAyMDc3LCAyMDc4LCAyMDc5LCAyMDgwLCAyMDgxLCAyMDgyLCAyMDgzLCAyMDg0LCAyMDg1LCAyMDg2LCAyMDg3LCAyMDg4LCAyMDg5LCAyMDkwLCAyMDkxLCAyMDkyLCAyMDkzLCAyMDk0LCAyMDk1LCAyMDk2LCAyMDk3LCAyMDk4LCAyMDk5LCAyMTAwLCAyMTAxLCAyMTAyLCAyMTAzLCAyMTA0LCAyMTA1LCAyMTA2LCAyMTA3LCAyMTA4LCAyMTA5LCAyMTEwLCAyMTExLCAyMTEyLCAyMTEzLCAyMTE0LCAyMTE1LCAyMTE2LCAyMTE3LCAyMTE4LCAyMTE5LCAyMTIwLCAyMTIxLCAyMTIyLCAyMTIzLCAyMTI0LCAyMTI1LCAyMTI2LCAyMTI3LCAyMTI4LCAyMTI5LCAyMTMwLCAyMTMxLCAyMTMyLCAyMTMzLCAyMTM0LCAyMTM1LCAyMTM2LCAyMTM3LCAyMTM4LCAyMTM5LCAyMTQwLCAyMTQxLCAyMTQyLCAyMTQzLCAyMTQ0LCAyMTQ1LCAyMTQ2LCAyMTQ3LCAyMTQ4LCAyMTQ5LCAyMTUwIF0sICJ0YWtlbkF0IjogIjIwMjMtMDktMTdUMTQ6NDU6NDMuODU5WiIsICJwb3N0ZWRBdCI6ICIyMDIzLTA5LTE3VDE0OjQ1OjQzLjg2MVoiLCAibW9kZWxWZXJzaW9uIjogIjAuMS4wIiwgImNvbmZpZ3VyYXRpb25Nb2RlbFZlcnNpb24iOiAiMC4xLjAiLCAidGltZXN0cmVhbSI6IHRydWUgfV0sImNsaWVudGlkIjoiZGV2X3BsY2ZfdGVzdHRlc3RfMDAyNyJ9",
                "approximateArrivalTimestamp": 1649781721.772,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49628516550903612936269980587021883789878662043055161346",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::093961187306:role/dev_plcf_glinojeckSFC_kinesis2timestream_lambda",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_glinojeckSFC_timeseries_data_stream",
        }
    ]
}
event_value_with_colon = {
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "6000fc03-2b97-40c3-b3ad-6cbbad51e26b",
                "sequenceNumber": "49628516550903612936269980587021883789878662043055161346",
                "data": "eyJkYXRhIjpbeyJkYXRhUG9pbnRJZCI6ImRhdGFwb2ludDpjb2xvbiIsInZhbHVlIjo3LCJ0YWtlbkF0IjoiMjAyMy0wOS0xN1QxNDo0NTo0My44NTlaIiwicG9zdGVkQXQiOiIyMDIzLTA5LTE3VDE0OjQ1OjQzLjg2MVoiLCJtb2RlbFZlcnNpb24iOiIwLjEuMCIsImNvbmZpZ3VyYXRpb25Nb2RlbFZlcnNpb24iOiIwLjEuMCIsInRpbWVzdHJlYW0iOnRydWV9XSwiY2xpZW50aWQiOiJkZXZfcGxjZl90ZXN0dGVzdF8wMDI3In0=",
                "approximateArrivalTimestamp": 1649781721.772,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49628516550903612936269980587021883789878662043055161346",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::093961187306:role/dev_plcf_glinojeckSFC_kinesis2timestream_lambda",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_glinojeckSFC_timeseries_data_stream",
        }
    ]
}
event_value_empty_str = {
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "6000fc03-2b97-40c3-b3ad-6cbbad51e26b",
                "sequenceNumber": "49628516550903612936269980587021883789878662043055161346",
                "data": "eyJkYXRhIjpbeyJkYXRhUG9pbnRJZCI6ImRhdGFwb2ludDpjb2xvbiIsInZhbHVlIjoiIiwidGFrZW5BdCI6IjIwMjMtMDktMTdUMTQ6NDU6NDMuODU5WiIsInBvc3RlZEF0IjoiMjAyMy0wOS0xN1QxNDo0NTo0My44NjFaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjp0cnVlfV0sImNsaWVudGlkIjoiZGV2X3BsY2ZfdGVzdHRlc3RfMDAyNyJ9",
                "approximateArrivalTimestamp": 1649781721.772,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49628516550903612936269980587021883789878662043055161346",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::093961187306:role/dev_plcf_glinojeckSFC_kinesis2timestream_lambda",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_glinojeckSFC_timeseries_data_stream",
        }
    ]
}
event_value_none = {
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "6000fc03-2b97-40c3-b3ad-6cbbad51e26b",
                "sequenceNumber": "49628516550903612936269980587021883789878662043055161346",
                "data": "eyJkYXRhIjpbeyJkYXRhUG9pbnRJZCI6ImRhdGFwb2ludDpjb2xvbiIsInZhbHVlIjpudWxsLCJ0YWtlbkF0IjoiMjAyMy0wOS0xN1QxNDo0NTo0My44NTlaIiwicG9zdGVkQXQiOiIyMDIzLTA5LTE3VDE0OjQ1OjQzLjg2MVoiLCJtb2RlbFZlcnNpb24iOiIwLjEuMCIsImNvbmZpZ3VyYXRpb25Nb2RlbFZlcnNpb24iOiIwLjEuMCIsInRpbWVzdHJlYW0iOnRydWV9XSwiY2xpZW50aWQiOiJkZXZfcGxjZl90ZXN0dGVzdF8wMDI3In0=",
                "approximateArrivalTimestamp": 1649781721.772,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49628516550903612936269980587021883789878662043055161346",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::093961187306:role/dev_plcf_glinojeckSFC_kinesis2timestream_lambda",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_glinojeckSFC_timeseries_data_stream",
        }
    ]
}

test_events_not_supported = [
    event_empty,
    event_value_string_to_long,
    event_value_with_colon,
    event_value_empty_str,
    event_value_none,
]

event_1 = {
    "Records": [
        {
            # {clientId: xxx, data: [array of 20 measurements with timestream: true]}
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "60927ab0-5427-4208-aebe-c720f182cf8b",
                "sequenceNumber": "49626676975634227302699157955443023644227873465234882562",
                "data": "eyJkYXRhIjpbeyJkYXRhUG9pbnRJZCI6IkNTMDMwM0hWX01WX1BWIiwidmFsdWUiOnRydWUsInRha2VuQXQiOiIyMDIyLTAyLTE0VDIwOjI1OjA4LjA1NFoiLCJwb3N0ZWRBdCI6IjIwMjItMDItMTRUMjA6MjU6MDguMDYwWiIsIm1vZGVsVmVyc2lvbiI6IjAuMS4wIiwiY29uZmlndXJhdGlvbk1vZGVsVmVyc2lvbiI6IjAuMS4wIiwidGltZXN0cmVhbSI6dHJ1ZX0seyJkYXRhUG9pbnRJZCI6IlRUMDMyMkhWX19PVVQiLCJ2YWx1ZSI6OC45Mzc4NDYxODM3NzY4NiwidGFrZW5BdCI6IjIwMjItMDItMTRUMjA6MjU6MDguMDU0WiIsInBvc3RlZEF0IjoiMjAyMi0wMi0xNFQyMDoyNTowOC4wNjBaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjp0cnVlfSx7ImRhdGFQb2ludElkIjoiREMwMzA4SFZfX09VVCIsInZhbHVlIjozNSwidGFrZW5BdCI6IjIwMjItMDItMTRUMjA6MjU6MDguMDU0WiIsInBvc3RlZEF0IjoiMjAyMi0wMi0xNFQyMDoyNTowOC4wNjFaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjp0cnVlfSx7ImRhdGFQb2ludElkIjoiQTNfV0RfQVBDX1ciLCJ2YWx1ZSI6ZmFsc2UsInRha2VuQXQiOiIyMDIyLTAyLTE0VDIwOjI1OjA4LjA1NFoiLCJwb3N0ZWRBdCI6IjIwMjItMDItMTRUMjA6MjU6MDguMDYxWiIsIm1vZGVsVmVyc2lvbiI6IjAuMS4wIiwiY29uZmlndXJhdGlvbk1vZGVsVmVyc2lvbiI6IjAuMS4wIiwidGltZXN0cmVhbSI6dHJ1ZX0seyJkYXRhUG9pbnRJZCI6Ik41MzAxSFZfU1BDIiwidmFsdWUiOnRydWUsInRha2VuQXQiOiIyMDIyLTAyLTE0VDIwOjI1OjA4LjA1NFoiLCJwb3N0ZWRBdCI6IjIwMjItMDItMTRUMjA6MjU6MDguMDYxWiIsIm1vZGVsVmVyc2lvbiI6IjAuMS4wIiwiY29uZmlndXJhdGlvbk1vZGVsVmVyc2lvbiI6IjAuMS4wIiwidGltZXN0cmVhbSI6dHJ1ZX0seyJkYXRhUG9pbnRJZCI6IkRDMDMwOEhWX19TVFIiLCJ2YWx1ZSI6dHJ1ZSwidGFrZW5BdCI6IjIwMjItMDItMTRUMjA6MjU6MDguMDU0WiIsInBvc3RlZEF0IjoiMjAyMi0wMi0xNFQyMDoyNTowOC4wNjFaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjp0cnVlfSx7ImRhdGFQb2ludElkIjoiREMwMzA4SFZfU1BDIiwidmFsdWUiOmZhbHNlLCJ0YWtlbkF0IjoiMjAyMi0wMi0xNFQyMDoyNTowOC4wNTRaIiwicG9zdGVkQXQiOiIyMDIyLTAyLTE0VDIwOjI1OjA4LjA2MVoiLCJtb2RlbFZlcnNpb24iOiIwLjEuMCIsImNvbmZpZ3VyYXRpb25Nb2RlbFZlcnNpb24iOiIwLjEuMCIsInRpbWVzdHJlYW0iOnRydWV9LHsiZGF0YVBvaW50SWQiOiJONTMwMUhfRkIxIiwidmFsdWUiOmZhbHNlLCJ0YWtlbkF0IjoiMjAyMi0wMi0xNFQyMDoyNTowOC4wNTRaIiwicG9zdGVkQXQiOiIyMDIyLTAyLTE0VDIwOjI1OjA4LjA2MVoiLCJtb2RlbFZlcnNpb24iOiIwLjEuMCIsImNvbmZpZ3VyYXRpb25Nb2RlbFZlcnNpb24iOiIwLjEuMCIsInRpbWVzdHJlYW0iOnRydWV9LHsiZGF0YVBvaW50SWQiOiJQQ1YwMzAxSFZfTVZfUFYiLCJ2YWx1ZSI6dHJ1ZSwidGFrZW5BdCI6IjIwMjItMDItMTRUMjA6MjU6MDguMDU0WiIsInBvc3RlZEF0IjoiMjAyMi0wMi0xNFQyMDoyNTowOC4wNjJaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjp0cnVlfSx7ImRhdGFQb2ludElkIjoiTEMwMzA0SFZfQ09ZIiwidmFsdWUiOjAsInRha2VuQXQiOiIyMDIyLTAyLTE0VDIwOjI1OjA4LjA1NFoiLCJwb3N0ZWRBdCI6IjIwMjItMDItMTRUMjA6MjU6MDguMDYzWiIsIm1vZGVsVmVyc2lvbiI6IjAuMS4wIiwiY29uZmlndXJhdGlvbk1vZGVsVmVyc2lvbiI6IjAuMS4wIiwidGltZXN0cmVhbSI6dHJ1ZX0seyJkYXRhUG9pbnRJZCI6IkNTMDMxNUhWX19GQjEiLCJ2YWx1ZSI6ZmFsc2UsInRha2VuQXQiOiIyMDIyLTAyLTE0VDIwOjI1OjA4LjA1NFoiLCJwb3N0ZWRBdCI6IjIwMjItMDItMTRUMjA6MjU6MDguMDYzWiIsIm1vZGVsVmVyc2lvbiI6IjAuMS4wIiwiY29uZmlndXJhdGlvbk1vZGVsVmVyc2lvbiI6IjAuMS4wIiwidGltZXN0cmVhbSI6dHJ1ZX0seyJkYXRhUG9pbnRJZCI6IldpckJfVHJfQmwiLCJ2YWx1ZSI6ZmFsc2UsInRha2VuQXQiOiIyMDIyLTAyLTE0VDIwOjI1OjA4LjA1NFoiLCJwb3N0ZWRBdCI6IjIwMjItMDItMTRUMjA6MjU6MDguMDYzWiIsIm1vZGVsVmVyc2lvbiI6IjAuMS4wIiwiY29uZmlndXJhdGlvbk1vZGVsVmVyc2lvbiI6IjAuMS4wIiwidGltZXN0cmVhbSI6dHJ1ZX0seyJkYXRhUG9pbnRJZCI6IkZDVjAzMjFIVl9PTlJFUSIsInZhbHVlIjpmYWxzZSwidGFrZW5BdCI6IjIwMjItMDItMTRUMjA6MjU6MDguMDU0WiIsInBvc3RlZEF0IjoiMjAyMi0wMi0xNFQyMDoyNTowOC4wNjRaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjp0cnVlfSx7ImRhdGFQb2ludElkIjoiQ1MwMzI2SFZfTVZfUFYiLCJ2YWx1ZSI6dHJ1ZSwidGFrZW5BdCI6IjIwMjItMDItMTRUMjA6MjU6MDguMDU0WiIsInBvc3RlZEF0IjoiMjAyMi0wMi0xNFQyMDoyNTowOC4wNjRaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjp0cnVlfSx7ImRhdGFQb2ludElkIjoiQ1MwMzE5SFZfX0ZCMSIsInZhbHVlIjpmYWxzZSwidGFrZW5BdCI6IjIwMjItMDItMTRUMjA6MjU6MDguMDU0WiIsInBvc3RlZEF0IjoiMjAyMi0wMi0xNFQyMDoyNTowOC4wNjRaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjp0cnVlfSx7ImRhdGFQb2ludElkIjoiQTNfV0RfQVBDX1IiLCJ2YWx1ZSI6dHJ1ZSwidGFrZW5BdCI6IjIwMjItMDItMTRUMjA6MjU6MDguMDU0WiIsInBvc3RlZEF0IjoiMjAyMi0wMi0xNFQyMDoyNTowOC4wNjVaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjp0cnVlfSx7ImRhdGFQb2ludElkIjoiTFQwMDM2SFZfX09VVCIsInZhbHVlIjoxLjAyNTI4MDIzNzE5Nzg4LCJ0YWtlbkF0IjoiMjAyMi0wMi0xNFQyMDoyNTowOC4wNTRaIiwicG9zdGVkQXQiOiIyMDIyLTAyLTE0VDIwOjI1OjA4LjA2NVoiLCJtb2RlbFZlcnNpb24iOiIwLjEuMCIsImNvbmZpZ3VyYXRpb25Nb2RlbFZlcnNpb24iOiIwLjEuMCIsInRpbWVzdHJlYW0iOnRydWV9LHsiZGF0YVBvaW50SWQiOiJMVDAwMDFIVl9fT1VUIiwidmFsdWUiOi0wLjYyNTAwMjM4NDE4NTc5MSwidGFrZW5BdCI6IjIwMjItMDItMTRUMjA6MjU6MDguMDU0WiIsInBvc3RlZEF0IjoiMjAyMi0wMi0xNFQyMDoyNTowOC4wNjVaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjp0cnVlfSx7ImRhdGFQb2ludElkIjoiTEMwMzA0SFZfU1BDIiwidmFsdWUiOmZhbHNlLCJ0YWtlbkF0IjoiMjAyMi0wMi0xNFQyMDoyNTowOC4wNTRaIiwicG9zdGVkQXQiOiIyMDIyLTAyLTE0VDIwOjI1OjA4LjA2NVoiLCJtb2RlbFZlcnNpb24iOiIwLjEuMCIsImNvbmZpZ3VyYXRpb25Nb2RlbFZlcnNpb24iOiIwLjEuMCIsInRpbWVzdHJlYW0iOnRydWV9LHsiZGF0YVBvaW50SWQiOiJDUzAzMjRIVl9NVl9QViIsInZhbHVlIjp0cnVlLCJ0YWtlbkF0IjoiMjAyMi0wMi0xNFQyMDoyNTowMC4wNTRaIiwicG9zdGVkQXQiOiIyMDIyLTAyLTE0VDIwOjI1OjA4LjA2NVoiLCJtb2RlbFZlcnNpb24iOiIwLjEuMCIsImNvbmZpZ3VyYXRpb25Nb2RlbFZlcnNpb24iOiIwLjEuMCIsInRpbWVzdHJlYW0iOnRydWV9XSwiY2xpZW50aWQiOiJkZXZfcGxjZl9nbGlub2plY2tTRkNfMDAwMSJ9",
                "approximateArrivalTimestamp": 1644870308.715,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49626676975634227302699157955443023644227873465234882562",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::093961187306:role/timestream_test",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_glinojeckSFC_timestream_test_data_stream",
        },
        {
            # {clientId: xxx, data: [array of 2 measurements with not timestream value]}
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "78441907-9d2e-4202-832d-4fdf9ee756e7",
                "sequenceNumber": "49626676975634227302699157955926593972073725135117352962",
                "data": "eyJkYXRhIjpbeyJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJkYXRhUG9pbnRJZCI6IkEzX1dEX0FQQ19SX0NPREVTWVMiLCJtb2RlbFZlcnNpb24iOiIwLjEuMCIsInBvc3RlZEF0IjoiMjAyMi0wMi0xNFQyMDoyNTowNy45NzRaIiwidGFrZW5BdCI6IjIwMjItMDItMTRUMjA6MjU6MDcuOTc0WiIsInZhbHVlIjp0cnVlfSx7ImNvbmZpZ3VyYXRpb25Nb2RlbFZlcnNpb24iOiIwLjEuMCIsImRhdGFQb2ludElkIjoiQTNfV0RfQVBDX1JfQ09ERVNZUyIsIm1vZGVsVmVyc2lvbiI6IjAuMS4wIiwicG9zdGVkQXQiOiIyMDIyLTAyLTE0VDIwOjI1OjA4Ljk3NFoiLCJ0YWtlbkF0IjoiMjAyMi0wMi0xNFQyMDoyNTowOC45NzRaIiwidmFsdWUiOmZhbHNlfV0sImNsaWVudGlkIjoiZGV2X3BsY2ZfZ2xpbm9qZWNrU0ZDXzAwMDEifQ==",
                "approximateArrivalTimestamp": 1644870309.061,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49626676975634227302699157955926593972073725135117352962",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::093961187306:role/timestream_test",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_glinojeckSFC_timestream_test_data_stream",
        },
    ]
}
result_1 = [
    call(
        DatabaseName="mockeddatabase",
        TableName="tabdefault",
        Records=[
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "CS0324HV_MV_PV",
                "MeasureValue": "True",
                "MeasureValueType": "BOOLEAN",
                "Time": "1644870300054",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "CS0303HV_MV_PV",
                "MeasureValue": "True",
                "MeasureValueType": "BOOLEAN",
                "Time": "1644870308054",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "TT0322HV__OUT",
                "MeasureValue": "8.93784618377686",
                "MeasureValueType": "DOUBLE",
                "Time": "1644870308054",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "DC0308HV__OUT",
                "MeasureValue": "35",
                "MeasureValueType": "DOUBLE",
                "Time": "1644870308054",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "A3_WD_APC_W",
                "MeasureValue": "False",
                "MeasureValueType": "BOOLEAN",
                "Time": "1644870308054",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "N5301HV_SPC",
                "MeasureValue": "True",
                "MeasureValueType": "BOOLEAN",
                "Time": "1644870308054",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "DC0308HV__STR",
                "MeasureValue": "True",
                "MeasureValueType": "BOOLEAN",
                "Time": "1644870308054",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "DC0308HV_SPC",
                "MeasureValue": "False",
                "MeasureValueType": "BOOLEAN",
                "Time": "1644870308054",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "N5301H_FB1",
                "MeasureValue": "False",
                "MeasureValueType": "BOOLEAN",
                "Time": "1644870308054",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "PCV0301HV_MV_PV",
                "MeasureValue": "True",
                "MeasureValueType": "BOOLEAN",
                "Time": "1644870308054",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "LC0304HV_COY",
                "MeasureValue": "0",
                "MeasureValueType": "DOUBLE",
                "Time": "1644870308054",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "CS0315HV__FB1",
                "MeasureValue": "False",
                "MeasureValueType": "BOOLEAN",
                "Time": "1644870308054",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "WirB_Tr_Bl",
                "MeasureValue": "False",
                "MeasureValueType": "BOOLEAN",
                "Time": "1644870308054",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "FCV0321HV_ONREQ",
                "MeasureValue": "False",
                "MeasureValueType": "BOOLEAN",
                "Time": "1644870308054",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "CS0326HV_MV_PV",
                "MeasureValue": "True",
                "MeasureValueType": "BOOLEAN",
                "Time": "1644870308054",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "CS0319HV__FB1",
                "MeasureValue": "False",
                "MeasureValueType": "BOOLEAN",
                "Time": "1644870308054",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "A3_WD_APC_R",
                "MeasureValue": "True",
                "MeasureValueType": "BOOLEAN",
                "Time": "1644870308054",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "LT0036HV__OUT",
                "MeasureValue": "1.02528023719788",
                "MeasureValueType": "DOUBLE",
                "Time": "1644870308054",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "LT0001HV__OUT",
                "MeasureValue": "-0.625002384185791",
                "MeasureValueType": "DOUBLE",
                "Time": "1644870308054",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "LC0304HV_SPC",
                "MeasureValue": "False",
                "MeasureValueType": "BOOLEAN",
                "Time": "1644870308054",
            },
        ],
        CommonAttributes={},
    )
]

event_with_device_name = {
    "Records": [
        {
            # {clientId: xxx, data: [array of 5 measurements with timestream: true]}, 3 with deviceName: "kaczuszka3", one with deviceName: "kaczuszka1", one with no deviceName
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "60927ab0-5427-4208-aebe-c720f182cf8b",
                "sequenceNumber": "49626676975634227302699157955443023644227873465234882562",
                "data": "eyJjbGllbnRpZCI6ICJkZXZfcGxjZl9nbGlub2plY2tTRkNfMDAwMSIsICJkYXRhIjogW3siY29uZmlndXJhdGlvbk1vZGVsVmVyc2lvbiI6ICIwLjEuMCIsICJkYXRhUG9pbnRJZCI6ICJDUzAzMDNIVl9NVl9QViIsICJkZXZpY2VOYW1lIjogImthY3p1c3prYTMiLCAibW9kZWxWZXJzaW9uIjogIjAuMS4wIiwgInBvc3RlZEF0IjogIjIwMjItMDItMTRUMjA6MjU6MDguMDYwWiIsICJ0YWtlbkF0IjogIjIwMjItMDItMTRUMjA6MjU6MDguMDU0WiIsICJ0aW1lc3RyZWFtIjogdHJ1ZSwgInZhbHVlIjogdHJ1ZX0sIHsiY29uZmlndXJhdGlvbk1vZGVsVmVyc2lvbiI6ICIwLjEuMCIsICJkYXRhUG9pbnRJZCI6ICJUVDAzMjJIVl9fT1VUIiwgImRldmljZU5hbWUiOiAia2FjenVzemthMyIsICJtb2RlbFZlcnNpb24iOiAiMC4xLjAiLCAicG9zdGVkQXQiOiAiMjAyMi0wMi0xNFQyMDoyNTowOC4wNjBaIiwgInRha2VuQXQiOiAiMjAyMi0wMi0xNFQyMDoyNTowOC4wNTRaIiwgInRpbWVzdHJlYW0iOiB0cnVlLCAidmFsdWUiOiA4LjkzNzg0NjE4Mzc3Njg2fSwgeyJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjogIjAuMS4wIiwgImRhdGFQb2ludElkIjogIkRDMDMwOEhWX19PVVQiLCAiZGV2aWNlTmFtZSI6ICJrYWN6dXN6a2EzIiwgIm1vZGVsVmVyc2lvbiI6ICIwLjEuMCIsICJwb3N0ZWRBdCI6ICIyMDIyLTAyLTE0VDIwOjI1OjA4LjA2MVoiLCAidGFrZW5BdCI6ICIyMDIyLTAyLTE0VDIwOjI1OjA4LjA1NFoiLCAidGltZXN0cmVhbSI6IHRydWUsICJ2YWx1ZSI6IDM1fSwgeyJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjogIjAuMS4wIiwgImRhdGFQb2ludElkIjogIk41MzAxSFZfU1BDIiwgImRldmljZU5hbWUiOiAia2FjenVzemthMSIsICJtb2RlbFZlcnNpb24iOiAiMC4xLjAiLCAicG9zdGVkQXQiOiAiMjAyMi0wMi0xNFQyMDoyNTowOC4wNjFaIiwgInRha2VuQXQiOiAiMjAyMi0wMi0xNFQyMDoyNTowOC4wNTRaIiwgInRpbWVzdHJlYW0iOiB0cnVlLCAidmFsdWUiOiB0cnVlfSwgeyJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjogIjAuMS4wIiwgImRhdGFQb2ludElkIjogIkRDMDMwOEhWX19TVFIiLCAibW9kZWxWZXJzaW9uIjogIjAuMS4wIiwgInBvc3RlZEF0IjogIjIwMjItMDItMTRUMjA6MjU6MDguMDYxWiIsICJ0YWtlbkF0IjogIjIwMjItMDItMTRUMjA6MjU6MDguMDU0WiIsICJ0aW1lc3RyZWFtIjogdHJ1ZSwgInZhbHVlIjogdHJ1ZX1dfQ==",
                "approximateArrivalTimestamp": 1644870308.715,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49626676975634227302699157955443023644227873465234882562",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::093961187306:role/timestream_test",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_glinojeckSFC_timestream_test_data_stream",
        }
    ]
}
event_with_device_name_result = [
    call(
        DatabaseName="mockeddatabase",
        TableName="tabprefix_kaczuszka3",
        Records=[
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "CS0303HV_MV_PV",
                "MeasureValue": "True",
                "MeasureValueType": "BOOLEAN",
                "Time": "1644870308054",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "TT0322HV__OUT",
                "MeasureValue": "8.93784618377686",
                "MeasureValueType": "DOUBLE",
                "Time": "1644870308054",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "DC0308HV__OUT",
                "MeasureValue": "35",
                "MeasureValueType": "DOUBLE",
                "Time": "1644870308054",
            },
        ],
        CommonAttributes={},
    ),
    call(
        DatabaseName="mockeddatabase",
        TableName="tabprefix_kaczuszka1",
        Records=[
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "N5301HV_SPC",
                "MeasureValue": "True",
                "MeasureValueType": "BOOLEAN",
                "Time": "1644870308054",
            }
        ],
        CommonAttributes={},
    ),
    call(
        DatabaseName="mockeddatabase",
        TableName="tabdefault",
        Records=[
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "DC0308HV__STR",
                "MeasureValue": "True",
                "MeasureValueType": "BOOLEAN",
                "Time": "1644870308054",
            }
        ],
        CommonAttributes={},
    ),
]
event_with_device_name_error_result = [
    call(
        Body="[{'Dimensions': [{'Name': 'factory', 'Value': 'mockfactory'}], 'MeasureName': 'CS0303HV_MV_PV', 'MeasureValue': 'True', 'MeasureValueType': 'BOOLEAN', 'Time': '1644870308054'}, {'Dimensions': [{'Name': 'factory', 'Value': 'mockfactory'}], 'MeasureName': 'TT0322HV__OUT', 'MeasureValue': '8.93784618377686', 'MeasureValueType': 'DOUBLE', 'Time': '1644870308054'}, {'Dimensions': [{'Name': 'factory', 'Value': 'mockfactory'}], 'MeasureName': 'DC0308HV__OUT', 'MeasureValue': '35', 'MeasureValueType': 'DOUBLE', 'Time': '1644870308054'}]",
        Bucket="error-mock-bucket",
        Key="errors/mockfactory-kinesis2timestream/tabprefix_kaczuszka3-123-123",
        ContentType="text/plain",
    ),
    call(
        Body="[{'Dimensions': [{'Name': 'factory', 'Value': 'mockfactory'}], 'MeasureName': 'N5301HV_SPC', 'MeasureValue': 'True', 'MeasureValueType': 'BOOLEAN', 'Time': '1644870308054'}]",
        Bucket="error-mock-bucket",
        Key="errors/mockfactory-kinesis2timestream/tabprefix_kaczuszka1-123-123",
        ContentType="text/plain",
    ),
    call(
        Body="[{'Dimensions': [{'Name': 'factory', 'Value': 'mockfactory'}], 'MeasureName': 'DC0308HV__STR', 'MeasureValue': 'True', 'MeasureValueType': 'BOOLEAN', 'Time': '1644870308054'}]",
        Bucket="error-mock-bucket",
        Key="errors/mockfactory-kinesis2timestream/tabdefault-123-123",
        ContentType="text/plain",
    ),
]

event_aggregated_measurements_as_value_with_clientid_short = {
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "7ab58511-d0e1-4788-af92-38564c91bd68",
                "sequenceNumber": "49628516550903612936269980591683501750312721068989612034",
                "data": "eyJkYXRhIjp7ImRhdGFQb2ludElkIjoiTFQwMDM2SFZfX09VVCIsInZhbHVlIjo1MC4wMTA1MiwidGFrZW5BdCI6IjIwMjItMDQtMTJUMTY6NTM6NTAuOTA0WiIsInBvc3RlZEF0IjoiMjAyMi0wNC0xMlQxNjo1Mzo1My44MDZaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjp0cnVlfSwiY2xpZW50aWQiOiJkZXZfcGxjZl9nbGlub2plY2tTRkNfMDAwMSJ9",
                "approximateArrivalTimestamp": 1649782434.048,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49628516550903612936269980591683501750312721068989612034",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::093961187306:role/dev_plcf_glinojeckSFC_kinesis2timestream_lambda",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_glinojeckSFC_timeseries_data_stream",
        },
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "ca0b3f02-bd46-46bc-aeed-bd1424079479",
                "sequenceNumber": "49628516550903612936269980591684710676132335698164318210",
                "data": "eyJkYXRhIjp7ImRhdGFQb2ludElkIjoiUFQwMzAySFZfX09VVCIsInZhbHVlIjoyNC45ODg0OSwidGFrZW5BdCI6IjIwMjItMDQtMTJUMTY6NTM6NTAuOTA0WiIsInBvc3RlZEF0IjoiMjAyMi0wNC0xMlQxNjo1Mzo1My44MDRaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjp0cnVlfSwiY2xpZW50aWQiOiJkZXZfcGxjZl9nbGlub2plY2tTRkNfMDAwMSJ9",
                "approximateArrivalTimestamp": 1649782434.049,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49628516550903612936269980591684710676132335698164318210",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::093961187306:role/dev_plcf_glinojeckSFC_kinesis2timestream_lambda",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_glinojeckSFC_timeseries_data_stream",
        },
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "1e1f138c-bdad-4b37-addd-445fb7de9097",
                "sequenceNumber": "49628516550903612936269980591685919601951950327339024386",
                "data": "eyJkYXRhIjp7ImRhdGFQb2ludElkIjoiTFQwMDMwSFZfX09VVCIsInZhbHVlIjo1OC4yNTQ5MDYsInRha2VuQXQiOiIyMDIyLTA0LTEyVDE2OjUzOjUwLjkwNFoiLCJwb3N0ZWRBdCI6IjIwMjItMDQtMTJUMTY6NTM6NTMuODA2WiIsIm1vZGVsVmVyc2lvbiI6IjAuMS4wIiwiY29uZmlndXJhdGlvbk1vZGVsVmVyc2lvbiI6IjAuMS4wIiwidGltZXN0cmVhbSI6dHJ1ZX0sImNsaWVudGlkIjoiZGV2X3BsY2ZfZ2xpbm9qZWNrU0ZDXzAwMDEifQ==",
                "approximateArrivalTimestamp": 1649782434.05,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49628516550903612936269980591685919601951950327339024386",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::093961187306:role/dev_plcf_glinojeckSFC_kinesis2timestream_lambda",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_glinojeckSFC_timeseries_data_stream",
        },
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "2537e392-5910-4ddc-a6b9-b16ead67a4f6",
                "sequenceNumber": "49628516550903612936269980591687128527771564956513730562",
                "data": "eyJkYXRhIjp7ImRhdGFQb2ludElkIjoiTFQwMzA0SFZfX09VVCIsInZhbHVlIjo4Ny41MDcwMiwidGFrZW5BdCI6IjIwMjItMDQtMTJUMTY6NTM6NTAuOTA0WiIsInBvc3RlZEF0IjoiMjAyMi0wNC0xMlQxNjo1Mzo1My44MDZaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjp0cnVlfSwiY2xpZW50aWQiOiJkZXZfcGxjZl9nbGlub2plY2tTRkNfMDAwMSJ9",
                "approximateArrivalTimestamp": 1649782434.051,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49628516550903612936269980591687128527771564956513730562",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::093961187306:role/dev_plcf_glinojeckSFC_kinesis2timestream_lambda",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_glinojeckSFC_timeseries_data_stream",
        },
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "c7405211-3eee-4264-81a3-d8754531c7f1",
                "sequenceNumber": "49628516550903612936269980591688337453591179585688436738",
                "data": "eyJkYXRhIjp7ImRhdGFQb2ludElkIjoiTFQwMDAxSFZfX09VVCIsInZhbHVlIjo5LjM1NjI3LCJ0YWtlbkF0IjoiMjAyMi0wNC0xMlQxNjo1Mzo1MC45MDRaIiwicG9zdGVkQXQiOiIyMDIyLTA0LTEyVDE2OjUzOjUzLjgwNloiLCJtb2RlbFZlcnNpb24iOiIwLjEuMCIsImNvbmZpZ3VyYXRpb25Nb2RlbFZlcnNpb24iOiIwLjEuMCIsInRpbWVzdHJlYW0iOnRydWV9LCJjbGllbnRpZCI6ImRldl9wbGNmX2dsaW5vamVja1NGQ18wMDAxIn0=",
                "approximateArrivalTimestamp": 1649782434.052,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49628516550903612936269980591688337453591179585688436738",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::093961187306:role/dev_plcf_glinojeckSFC_kinesis2timestream_lambda",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_glinojeckSFC_timeseries_data_stream",
        },
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "d982ebbe-4648-40a7-873d-491da1419dbd",
                "sequenceNumber": "49628516550903612936269980591689546379410794214863142914",
                "data": "eyJkYXRhIjpbeyJkYXRhUG9pbnRJZCI6IlBDMDMwMkhWX19TTUEiLCJ2YWx1ZSI6bnVsbCwidGFrZW5BdCI6IjIwMjItMDQtMTJUMTY6NTM6NTAuOTA0WiIsInBvc3RlZEF0IjoiMjAyMi0wNC0xMlQxNjo1Mzo1My43OTRaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjp0cnVlfSx7ImRhdGFQb2ludElkIjoiUEMwMzAxSFZfX1NJRSIsInZhbHVlIjpudWxsLCJ0YWtlbkF0IjoiMjAyMi0wNC0xMlQxNjo1Mzo1MC45MDRaIiwicG9zdGVkQXQiOiIyMDIyLTA0LTEyVDE2OjUzOjUzLjc5NFoiLCJtb2RlbFZlcnNpb24iOiIwLjEuMCIsImNvbmZpZ3VyYXRpb25Nb2RlbFZlcnNpb24iOiIwLjEuMCIsInRpbWVzdHJlYW0iOnRydWV9LHsiZGF0YVBvaW50SWQiOiJQQzAzMDFIVl9fU01BIiwidmFsdWUiOm51bGwsInRha2VuQXQiOiIyMDIyLTA0LTEyVDE2OjUzOjUwLjkwNFoiLCJwb3N0ZWRBdCI6IjIwMjItMDQtMTJUMTY6NTM6NTMuNzk1WiIsIm1vZGVsVmVyc2lvbiI6IjAuMS4wIiwiY29uZmlndXJhdGlvbk1vZGVsVmVyc2lvbiI6IjAuMS4wIiwidGltZXN0cmVhbSI6dHJ1ZX0seyJkYXRhUG9pbnRJZCI6IkNTMDM5N0hWX09OUkVRIiwidmFsdWUiOmZhbHNlLCJ0YWtlbkF0IjoiMjAyMi0wNC0xMlQxNjo1Mzo1MC45MDRaIiwicG9zdGVkQXQiOiIyMDIyLTA0LTEyVDE2OjUzOjUzLjc5NVoiLCJtb2RlbFZlcnNpb24iOiIwLjEuMCIsImNvbmZpZ3VyYXRpb25Nb2RlbFZlcnNpb24iOiIwLjEuMCIsInRpbWVzdHJlYW0iOnRydWV9LHsiZGF0YVBvaW50SWQiOiJDUzAzMTdIVl9PTlJFUSIsInZhbHVlIjpmYWxzZSwidGFrZW5BdCI6IjIwMjItMDQtMTJUMTY6NTM6NTAuOTA0WiIsInBvc3RlZEF0IjoiMjAyMi0wNC0xMlQxNjo1Mzo1My43OTZaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjp0cnVlfSx7ImRhdGFQb2ludElkIjoiQ1MwMzE4SFZfT05SRVEiLCJ2YWx1ZSI6ZmFsc2UsInRha2VuQXQiOiIyMDIyLTA0LTEyVDE2OjUzOjUwLjkwNFoiLCJwb3N0ZWRBdCI6IjIwMjItMDQtMTJUMTY6NTM6NTMuNzk2WiIsIm1vZGVsVmVyc2lvbiI6IjAuMS4wIiwiY29uZmlndXJhdGlvbk1vZGVsVmVyc2lvbiI6IjAuMS4wIiwidGltZXN0cmVhbSI6dHJ1ZX0seyJkYXRhUG9pbnRJZCI6IkNTMDMzM0hWX09OUkVRIiwidmFsdWUiOmZhbHNlLCJ0YWtlbkF0IjoiMjAyMi0wNC0xMlQxNjo1Mzo1MC45MDRaIiwicG9zdGVkQXQiOiIyMDIyLTA0LTEyVDE2OjUzOjUzLjc5NloiLCJtb2RlbFZlcnNpb24iOiIwLjEuMCIsImNvbmZpZ3VyYXRpb25Nb2RlbFZlcnNpb24iOiIwLjEuMCIsInRpbWVzdHJlYW0iOnRydWV9LHsiZGF0YVBvaW50SWQiOiJDUzAzMTlIVl9PTlJFUSIsInZhbHVlIjpmYWxzZSwidGFrZW5BdCI6IjIwMjItMDQtMTJUMTY6NTM6NTAuOTA0WiIsInBvc3RlZEF0IjoiMjAyMi0wNC0xMlQxNjo1Mzo1My43OTZaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjp0cnVlfSx7ImRhdGFQb2ludElkIjoiQ1MwMzEzSFZfT05SRVEiLCJ2YWx1ZSI6ZmFsc2UsInRha2VuQXQiOiIyMDIyLTA0LTEyVDE2OjUzOjUwLjkwNFoiLCJwb3N0ZWRBdCI6IjIwMjItMDQtMTJUMTY6NTM6NTMuNzk2WiIsIm1vZGVsVmVyc2lvbiI6IjAuMS4wIiwiY29uZmlndXJhdGlvbk1vZGVsVmVyc2lvbiI6IjAuMS4wIiwidGltZXN0cmVhbSI6dHJ1ZX0seyJkYXRhUG9pbnRJZCI6IkNTMDMxNUhWX09OUkVRIiwidmFsdWUiOmZhbHNlLCJ0YWtlbkF0IjoiMjAyMi0wNC0xMlQxNjo1Mzo1MC45MDRaIiwicG9zdGVkQXQiOiIyMDIyLTA0LTEyVDE2OjUzOjUzLjc5NloiLCJtb2RlbFZlcnNpb24iOiIwLjEuMCIsImNvbmZpZ3VyYXRpb25Nb2RlbFZlcnNpb24iOiIwLjEuMCIsInRpbWVzdHJlYW0iOnRydWV9LHsiZGF0YVBvaW50SWQiOiJDUzAzMTZIVl9PTlJFUSIsInZhbHVlIjpmYWxzZSwidGFrZW5BdCI6IjIwMjItMDQtMTJUMTY6NTM6NTAuOTA0WiIsInBvc3RlZEF0IjoiMjAyMi0wNC0xMlQxNjo1Mzo1My43OTZaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjp0cnVlfSx7ImRhdGFQb2ludElkIjoiQ1MwMzI0SFZfT05SRVEiLCJ2YWx1ZSI6ZmFsc2UsInRha2VuQXQiOiIyMDIyLTA0LTEyVDE2OjUzOjUwLjkwNFoiLCJwb3N0ZWRBdCI6IjIwMjItMDQtMTJUMTY6NTM6NTMuNzk2WiIsIm1vZGVsVmVyc2lvbiI6IjAuMS4wIiwiY29uZmlndXJhdGlvbk1vZGVsVmVyc2lvbiI6IjAuMS4wIiwidGltZXN0cmVhbSI6dHJ1ZX0seyJkYXRhUG9pbnRJZCI6IkNTMDMyNkhWX09OUkVRIiwidmFsdWUiOmZhbHNlLCJ0YWtlbkF0IjoiMjAyMi0wNC0xMlQxNjo1Mzo1MC45MDRaIiwicG9zdGVkQXQiOiIyMDIyLTA0LTEyVDE2OjUzOjUzLjc5N1oiLCJtb2RlbFZlcnNpb24iOiIwLjEuMCIsImNvbmZpZ3VyYXRpb25Nb2RlbFZlcnNpb24iOiIwLjEuMCIsInRpbWVzdHJlYW0iOnRydWV9LHsiZGF0YVBvaW50SWQiOiJDUzAzMjBIVl9PTlJFUSIsInZhbHVlIjp0cnVlLCJ0YWtlbkF0IjoiMjAyMi0wNC0xMlQxNjo1Mzo1MC45MDRaIiwicG9zdGVkQXQiOiIyMDIyLTA0LTEyVDE2OjUzOjUzLjc5N1oiLCJtb2RlbFZlcnNpb24iOiIwLjEuMCIsImNvbmZpZ3VyYXRpb25Nb2RlbFZlcnNpb24iOiIwLjEuMCIsInRpbWVzdHJlYW0iOnRydWV9LHsiZGF0YVBvaW50SWQiOiJDUzAzMTRIVl9PTlJFUSIsInZhbHVlIjpmYWxzZSwidGFrZW5BdCI6IjIwMjItMDQtMTJUMTY6NTM6NTAuOTA0WiIsInBvc3RlZEF0IjoiMjAyMi0wNC0xMlQxNjo1Mzo1My43OTdaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjp0cnVlfSx7ImRhdGFQb2ludElkIjoiQ1MwMzAzSFZfT05SRVEiLCJ2YWx1ZSI6ZmFsc2UsInRha2VuQXQiOiIyMDIyLTA0LTEyVDE2OjUzOjUwLjkwNFoiLCJwb3N0ZWRBdCI6IjIwMjItMDQtMTJUMTY6NTM6NTMuNzk3WiIsIm1vZGVsVmVyc2lvbiI6IjAuMS4wIiwiY29uZmlndXJhdGlvbk1vZGVsVmVyc2lvbiI6IjAuMS4wIiwidGltZXN0cmVhbSI6dHJ1ZX0seyJkYXRhUG9pbnRJZCI6IlBDMDMwMkhWX19TSUUiLCJ2YWx1ZSI6bnVsbCwidGFrZW5BdCI6IjIwMjItMDQtMTJUMTY6NTM6NTAuOTA0WiIsInBvc3RlZEF0IjoiMjAyMi0wNC0xMlQxNjo1Mzo1My44MDJaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjp0cnVlfSx7ImRhdGFQb2ludElkIjoiTEMwMzA0SFZfTVZfT1QiLCJ2YWx1ZSI6MCwidGFrZW5BdCI6IjIwMjItMDQtMTJUMTY6NTM6NTAuOTA0WiIsInBvc3RlZEF0IjoiMjAyMi0wNC0xMlQxNjo1Mzo1My44MDVaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjp0cnVlfSx7ImRhdGFQb2ludElkIjoiUENWMDMwMUhWX0NPWSIsInZhbHVlIjo0OC44NDg5NiwidGFrZW5BdCI6IjIwMjItMDQtMTJUMTY6NTM6NTAuOTA0WiIsInBvc3RlZEF0IjoiMjAyMi0wNC0xMlQxNjo1Mzo1My44MDVaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjp0cnVlfSx7ImRhdGFQb2ludElkIjoiUENWMDMwMkhWX0NPWSIsInZhbHVlIjoxOS41NjE2NzIsInRha2VuQXQiOiIyMDIyLTA0LTEyVDE2OjUzOjUwLjkwNFoiLCJwb3N0ZWRBdCI6IjIwMjItMDQtMTJUMTY6NTM6NTMuODA1WiIsIm1vZGVsVmVyc2lvbiI6IjAuMS4wIiwiY29uZmlndXJhdGlvbk1vZGVsVmVyc2lvbiI6IjAuMS4wIiwidGltZXN0cmVhbSI6dHJ1ZX1dLCJjbGllbnRpZCI6ImRldl9wbGNmX2dsaW5vamVja1NGQ18wMDAxIn0=",
                "approximateArrivalTimestamp": 1649782434.053,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49628516550903612936269980591689546379410794214863142914",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::093961187306:role/dev_plcf_glinojeckSFC_kinesis2timestream_lambda",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_glinojeckSFC_timeseries_data_stream",
        },
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "d4ce175d-7521-4bc5-9bc4-ace8e620ad6c",
                "sequenceNumber": "49628516550903612936269980591690755305230408844037849090",
                "data": "eyJkYXRhIjp7ImRhdGFQb2ludElkIjoiUEMwMzAxSFZfX09VVCIsInZhbHVlIjo5OS45OTkxMTUsInRha2VuQXQiOiIyMDIyLTA0LTEyVDE2OjUzOjUwLjkwNFoiLCJwb3N0ZWRBdCI6IjIwMjItMDQtMTJUMTY6NTM6NTMuODA1WiIsIm1vZGVsVmVyc2lvbiI6IjAuMS4wIiwiY29uZmlndXJhdGlvbk1vZGVsVmVyc2lvbiI6IjAuMS4wIiwidGltZXN0cmVhbSI6dHJ1ZX0sImNsaWVudGlkIjoiZGV2X3BsY2ZfZ2xpbm9qZWNrU0ZDXzAwMDEifQ==",
                "approximateArrivalTimestamp": 1649782434.055,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49628516550903612936269980591690755305230408844037849090",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::093961187306:role/dev_plcf_glinojeckSFC_kinesis2timestream_lambda",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_glinojeckSFC_timeseries_data_stream",
        },
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "595cc3e2-1cc9-4df8-bf8a-0f0dcab65518",
                "sequenceNumber": "49628516550903612936269980591691964231050023473212555266",
                "data": "eyJkYXRhIjp7ImRhdGFQb2ludElkIjoiTjUzMDFIX0FPVVQiLCJ2YWx1ZSI6NDUsInRha2VuQXQiOiIyMDIyLTA0LTEyVDE2OjUzOjUwLjkwNFoiLCJwb3N0ZWRBdCI6IjIwMjItMDQtMTJUMTY6NTM6NTMuODA1WiIsIm1vZGVsVmVyc2lvbiI6IjAuMS4wIiwiY29uZmlndXJhdGlvbk1vZGVsVmVyc2lvbiI6IjAuMS4wIiwidGltZXN0cmVhbSI6dHJ1ZX0sImNsaWVudGlkIjoiZGV2X3BsY2ZfZ2xpbm9qZWNrU0ZDXzAwMDEifQ==",
                "approximateArrivalTimestamp": 1649782434.055,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49628516550903612936269980591691964231050023473212555266",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::093961187306:role/dev_plcf_glinojeckSFC_kinesis2timestream_lambda",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_glinojeckSFC_timeseries_data_stream",
        },
    ]
}
event_aggregated___short_result = [
    call(
        DatabaseName="mockeddatabase",
        TableName="tabdefault",
        Records=[
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "LT0036HV__OUT",
                "MeasureValue": "50.01052",
                "MeasureValueType": "DOUBLE",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "PT0302HV__OUT",
                "MeasureValue": "24.98849",
                "MeasureValueType": "DOUBLE",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "LT0030HV__OUT",
                "MeasureValue": "58.254906",
                "MeasureValueType": "DOUBLE",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "LT0304HV__OUT",
                "MeasureValue": "87.50702",
                "MeasureValueType": "DOUBLE",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "LT0001HV__OUT",
                "MeasureValue": "9.35627",
                "MeasureValueType": "DOUBLE",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "CS0397HV_ONREQ",
                "MeasureValue": "False",
                "MeasureValueType": "BOOLEAN",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "CS0317HV_ONREQ",
                "MeasureValue": "False",
                "MeasureValueType": "BOOLEAN",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "CS0318HV_ONREQ",
                "MeasureValue": "False",
                "MeasureValueType": "BOOLEAN",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "CS0333HV_ONREQ",
                "MeasureValue": "False",
                "MeasureValueType": "BOOLEAN",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "CS0319HV_ONREQ",
                "MeasureValue": "False",
                "MeasureValueType": "BOOLEAN",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "CS0313HV_ONREQ",
                "MeasureValue": "False",
                "MeasureValueType": "BOOLEAN",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "CS0315HV_ONREQ",
                "MeasureValue": "False",
                "MeasureValueType": "BOOLEAN",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "CS0316HV_ONREQ",
                "MeasureValue": "False",
                "MeasureValueType": "BOOLEAN",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "CS0324HV_ONREQ",
                "MeasureValue": "False",
                "MeasureValueType": "BOOLEAN",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "CS0326HV_ONREQ",
                "MeasureValue": "False",
                "MeasureValueType": "BOOLEAN",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "CS0320HV_ONREQ",
                "MeasureValue": "True",
                "MeasureValueType": "BOOLEAN",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "CS0314HV_ONREQ",
                "MeasureValue": "False",
                "MeasureValueType": "BOOLEAN",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "CS0303HV_ONREQ",
                "MeasureValue": "False",
                "MeasureValueType": "BOOLEAN",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "LC0304HV_MV_OT",
                "MeasureValue": "0",
                "MeasureValueType": "DOUBLE",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "PCV0301HV_COY",
                "MeasureValue": "48.84896",
                "MeasureValueType": "DOUBLE",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "PCV0302HV_COY",
                "MeasureValue": "19.561672",
                "MeasureValueType": "DOUBLE",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "PC0301HV__OUT",
                "MeasureValue": "99.999115",
                "MeasureValueType": "DOUBLE",
                "Time": "1649782430904",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "mockfactory"}],
                "MeasureName": "N5301H_AOUT",
                "MeasureValue": "45",
                "MeasureValueType": "DOUBLE",
                "Time": "1649782430904",
            },
        ],
        CommonAttributes={},
    )
]

event_with_factoryid = {
    "Records": [
        {
            # {clientId: xxx, data: [array of 20 measurements with timestream: true]}
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "11145ab0-5427-4208-aebe-c720f182cc11",
                "sequenceNumber": "32121776975634227302699213955443023644227873465234882999",
                "data": "eyJkYXRhIjp7ImRhdGFQb2ludElkIjoiZjJmX3RydWNrX2lkIiwidmFsdWUiOjEyMzQ1NjcsInRha2VuQXQiOiIyMDI0LTEwLTEwVDA4OjIyOjI1LjU3MloiLCJwb3N0ZWRBdCI6IjIwMjQtMTAtMTBUMDg6MjI6MjYuOTQwWiIsIm1vZGVsVmVyc2lvbiI6IjAuMS4wIiwiY29uZmlndXJhdGlvbk1vZGVsVmVyc2lvbiI6IjAuMS4wIiwidGltZXN0cmVhbSI6IHRydWV9LCJjbGllbnRpZCI6ImRldl9wbGNmX2JlZXRsb2FkZXIwMDA5NSIsICJmYWN0b3J5aWQiOiJiZWV0bG9hZGVyMDAwOTUifQ==",
                "approximateArrivalTimestamp": 1644870308.715,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:32121776975634227302699213955443023644227873465234882999",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::093961187306:role/timestream_test",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_beetloaders_test_data_data_stream",
        },
        {
            # {clientId: xxx, data: [array of 20 measurements with timestream: true]}
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "22289ab0-5427-4208-aebe-c720f182ru22",
                "sequenceNumber": "58621776975634227302699213955443023644227873465234882345",
                "data": "eyJkYXRhIjp7ImRhdGFQb2ludElkIjoiZjJmX3BpbGVfbm8iLCJ2YWx1ZSI6MjM0NTY3OCwidGFrZW5BdCI6IjIwMjQtMTAtMTBUMDg6MjI6MjUuNTcyWiIsInBvc3RlZEF0IjoiMjAyNC0xMC0xMFQwODoyMjoyNi45NDBaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJ0aW1lc3RyZWFtIjogdHJ1ZX0sImNsaWVudGlkIjoiZGV2X3BsY2ZfYmVldGxvYWRlcjAwMDk1IiwgImZhY3RvcnlpZCI6ImJlZXRsb2FkZXIwMDA5NSJ9",
                "approximateArrivalTimestamp": 1644870308.717,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:58621776975634227302699213955443023644227873465234882345",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::093961187306:role/timestream_test",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_beetloaders_test_data_data_stream",
        },
        {
            # {clientId: xxx, data: [array of 20 measurements with timestream: true]}
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "33389ab0-5427-4208-aebe-c720f182ru33",
                "sequenceNumber": "11111776975634227302699213955443023644227873465234822222",
                "data": "eyJkYXRhIjp7ImRhdGFQb2ludElkIjoiZjJmX2xvYWRfbm8iLCJ2YWx1ZSI6MzQ1NjcsInRha2VuQXQiOiIyMDI0LTEwLTEwVDA4OjIyOjI1LjU3MloiLCJwb3N0ZWRBdCI6IjIwMjQtMTAtMTBUMDg6MjI6MjYuOTQwWiIsIm1vZGVsVmVyc2lvbiI6IjAuMS4wIiwiY29uZmlndXJhdGlvbk1vZGVsVmVyc2lvbiI6IjAuMS4wIiwidGltZXN0cmVhbSI6IHRydWV9LCJjbGllbnRpZCI6ImRldl9wbGNmX2JlZXRsb2FkZXIwMDA5NSIsICJmYWN0b3J5aWQiOiJiZWV0bG9hZGVyMDAwOTUifQ==",
                "approximateArrivalTimestamp": 1644870308.717,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:11111776975634227302699213955443023644227873465234822222",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::093961187306:role/timestream_test",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_beetloaders_test_data_data_stream",
        },
    ]
}

result_with_factoryid = [
    call(
        DatabaseName="mockeddatabase",
        TableName="tabdefault",
        Records=[
            {
                "Dimensions": [{"Name": "factory", "Value": "beetloader00095"}],
                "MeasureName": "f2f_truck_id",
                "MeasureValue": "1234567",
                "MeasureValueType": "DOUBLE",
                "Time": "1728548545572",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "beetloader00095"}],
                "MeasureName": "f2f_pile_no",
                "MeasureValue": "2345678",
                "MeasureValueType": "DOUBLE",
                "Time": "1728548545572",
            },
            {
                "Dimensions": [{"Name": "factory", "Value": "beetloader00095"}],
                "MeasureName": "f2f_load_no",
                "MeasureValue": "34567",
                "MeasureValueType": "DOUBLE",
                "Time": "1728548545572",
            },
        ],
        CommonAttributes={},
    )
]

test_events_with_timestream_calls = [
    (event_1, result_1),
    (event_with_device_name, event_with_device_name_result),
    (
        event_aggregated_measurements_as_value_with_clientid_short,
        event_aggregated___short_result,
    ),
    (event_with_factoryid, result_with_factoryid)
]


class MockRejectedRecordsException(Exception):
    def __init__(self, response):
        self.response = response


rejected_records_response = {
    "RejectedRecords": [{"RecordIndex": 0, "Reason": "Some reason"}]
}
