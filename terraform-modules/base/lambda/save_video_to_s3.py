from videostreams import videostreams


def lambda_handler(event, context):
    """
    Lists all Kinesis Video Streams, fetches videos of defined length and stores them into S3.
    """

    print(f"Starting Lambda for copying videos to S3, event = {event}")
    videostreams.initialize_clients()
    videostreams.process_streams(event)
