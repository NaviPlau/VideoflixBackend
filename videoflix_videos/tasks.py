from celery import shared_task
import subprocess
from videoflix_videos.models import Video
import os
import time
import logging
logger = logging.getLogger(__name__)

@shared_task
def convert_to_hls(video_id):
    """
    Convert a video to HLS format with multiple quality variants.

    This Celery task takes a video ID, retrieves the corresponding video
    object, and converts the video file to HLS format with multiple 
    quality variants using ffmpeg. The task generates four HLS 
    playlists with different resolutions and bitrates, and creates a 
    master playlist containing all variants.

    Args:
        video_id (int): The ID of the video to be converted.

    Logs:
        Info logs indicating the start and successful completion of the 
        conversion, as well as any commands run during the process.
        Error logs if any exceptions occur during the task execution.

    The converted HLS playlists are saved to the media storage, and the 
    video object is updated with the path to the master playlist.
    """

    logger.info(f"Starting HLS conversion for video ID: {video_id}")

    try:
        video = Video.objects.get(id=video_id)
        input_file = video.file.path
        output_dir = os.path.join('videos', 'hls', str(video.id))
        os.makedirs(output_dir, exist_ok=True)
        variants = [
            {'scale': '426x240', 'bitrate': '500k', 'variant': '0'},
            {'scale': '640x360', 'bitrate': '1000k', 'variant': '1'},
            {'scale': '1280x720', 'bitrate': '2500k', 'variant': '2'},
            {'scale': '1920x1080', 'bitrate': '5000k', 'variant': '3'}
        ]
        for v in variants:
            cmd = [
                '/usr/bin/ffmpeg', '-i', input_file,
                '-vf', f'scale={v["scale"]}',
                '-b:v', v['bitrate'], '-c:v', 'h264', '-preset', 'fast',
                '-c:a', 'aac', '-b:a', '128k',
                '-f', 'hls',
                '-hls_time', '5',
                '-hls_list_size', '0',
                '-hls_segment_filename', os.path.join(output_dir, f'segment_{v["variant"]}_%03d.ts'),
                os.path.join(output_dir, f'variant_{v["variant"]}.m3u8')
            ]

            logger.info(f"Running command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
        master_playlist = os.path.join(output_dir, 'master.m3u8')
        master_content = """
                #EXTM3U
                #EXT-X-STREAM-INF:BANDWIDTH=500000,RESOLUTION=426x240
                variant_0.m3u8
                #EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=640x360
                variant_1.m3u8
                #EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720
                variant_2.m3u8
                #EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080
                variant_3.m3u8
            """

        with open(master_playlist, 'w') as f:
            f.write(master_content.strip())
        video.hls_master_playlist = f"videos/hls/{video.id}/master.m3u8"

        video.save()
        logger.info(f"Successfully completed HLS conversion for video ID: {video_id}")

    except Exception as e:
        logger.error(f"Error in HLS conversion task: {e}")

@shared_task(queue='default')
def test_celery_task():
    """
    A simple Celery task for testing purposes.

    This task simulates a short delay and prints messages indicating
    the start and completion of the task.

    Returns:
        str: A message indicating that the task has completed.
    """

    print("Task started!")
    time.sleep(1)
    print("Task completed!")
    return "Task completed"
