import logging
from video_stream_data_archiver.video_stream_data_archiver import VideoStreamDataArchiver

logger = logging.getLogger("VideoStreamDataArchiver")
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def lambda_handler(event, context):
    """
    Lists all Kinesis Video Streams, fetches videos of defined length and stores them into S3.
    """
    videos = VideoStreamDataArchiver()
    videos.process_streams(event, context)
