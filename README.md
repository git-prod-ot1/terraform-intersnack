## Overview

Application architecture can be considered as two separate parts: the one responsible for processing measurement samples and configuration JSON messages, and the one dedicated to processing video streams.

Messages from LoopEdge flow into the cloud through AWS IoT Core, which passes them forward to AWS Kinesis Data Stream. In turn, AWS Kinesis Firehose Delivery Stream reads incoming messages, feeds them into AWS Lambda functions for any sort of validation or transformation and then stores them into AWS S3. Messages can be stored in plain JSONs or a dedicated binary format with the data schema described in AWS Glue.  
Measurement samples are stored in a binary format to improve querying efficiency.  
Configuration update messages are stored in plain JSON to facilitate further processing.  
Retained data can be relatively easy queried with the use of AWS Athena, a tool dedicated for searching through large volumes of semi-structured data kept in S3 and other data sources.

Video streams provided by factory cameras are fed into AWS Kinesis Video Streams. Periodically, an AWS Lambda function is run to read the video feeds and store consecutive video clips in S3.

## Detailed description and usage hints

Below you can find a more detailed description of things to have in mind when configuring and using the system.

### IoT Core
- Policy for a Certificate has to be configured with permissions required to connect and send messages to IoT Core. At the very least, client needs to have permissions for connecting to the IoT Core with a specific Client ID and publishing messages to a particular MQTT topic.
- Client IDs used by LoopEdge must be unique, so if LoopEdge connects to AWS IoT Core with two separates processes (e.g. one for sending measurement samples and the other for sending configuration updates), each process needs to have a unique Client ID

### Kinesis
- We assume that each factory will have a separate Data Stream and Firehose Delivery Stream. This decouples particular factories and makes them manageable more easily. In particular, it allows for independent scaling of streams, determined by the number of messages that given factory produces.
- Measurement samples are stored in a binary Parquet format. This improves performance when querying and reduces the size of stored objects.
- Configuration messages are stored in the original JSON format for two reasons. Firstly, we don't expect many messages of this kind during the system lifetime, so we wouldn't reap the benefits provided by the binary format. Moreover, we expect that these messages will be very often put together to generate the current configuration or any intermedia configurations. Storing this data in JSON makes it easier to make such operations with absolutely any tool even long time after messages were stored in S3.
- All messages are passed through Lambda functions to execute any transformations and validations required to accept and consume incoming data. At the most basic level, Lambda functions trim all string values, so there are no whitespaces at values boundaries and verify if there are no blank strings (considered invalid).
- Measurement samples data is partitioned by year/month/day. Partitioning the data down to the level of hours make it very inefficient to maintain the index as it creates a lot of relatively small index files crippling performance.
- When saving records as JSON, the entire JSON object needs to be formatted in a single line

### AWS Glue
- In order to convert incoming messages to the binary format, Kinesis Firehose requires a schema stored in AWS Glue service. Such schemas are generated can be either created manually or generated by Glue with the use of a crawler. In this project we create such schemas manually to gain full control over their operating details.

### Athena

- Athena is based on Presto querying engine in a relatively old version 0.172, so it's very useful to look into Presto documentation for syntax reference and available functions _for this particular version_.

### Kinesis Video Streams

A dedicated Lambda has been created for periodically iterating through all Kinesis Video Streams fed with video coming from cameras. 
- Lambda is invoked periodically with a cron job defined in CloudWatch Rules.
- Length of generated movies is configurable through Lambda environment variable and can be changed live without any data loss or video duplication. This interval is also independent of the Lambda invocation interval, but clearly it makes most sense for these periods to be equal.
- If for some reason Lambda function was not invoked, it should "catch up" with the stream on the next invocation.
- Bear in mind that AWS GetClip API puts some limitations on the size of the video which can be fetched from Kinesis Video Streams. It must not exceed 100 MB and 200 fragments. Fragment length should be set in GStreamer configuration at LoopEdge, so desired movie length fits into this limitation. For instance, setting it to 5 seconds allows for generating 1000s = 16:40 min of video.
- Every Lambda function has a timeout defined. If a Lambda function doesn't finish in a given time window, it gets aborted by AWS. This requires adjusting (most likely experimentally) the timeout period based on the number of Video Streams which need to be processed.

### S3

In total, 3 buckets are necessary:
- for measurement samples
- for configuration updates
- for video clips

Factories are separated in S3 on a directory level and not on bucket level, meaning that each factory exists in the same S3 bucket as a different directory. This approach makes it more convenient for running any sort of analysis as storing everything in a single place gives more flexibility in running company-wide analytics, while at the same time directory-level separation still provides a way to limit data research to a specific factory.

### Lambda

- All Lambdas are written in Python 3.8
- It's a Kinesis Firehose Delivery Stream recommendation for Lambdas to have a timeout of at least 60 seconds.
- Some Lambdas' properties are configurable through environment variables. Please refer to specific Lambda environment variables settings to see what can be changed without modifying the code.
