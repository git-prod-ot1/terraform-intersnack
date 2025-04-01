import logging
from video_stream_data_archiver.video_stream_data_archiver import VideoStreamDataArchiver

logger = logging.getLogger("VideoStreamDataArchiver")
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def lambda_handler(event, context):
    """
    Fetches videos of defined length and stores them into S3...
    """
    videos = VideoStreamDataArchiver()
    videos.get_clips(event, context)

