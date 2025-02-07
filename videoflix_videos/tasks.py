from celery import shared_task
import subprocess
from videoflix_videos.models import Video
import os
import time
import logging
logger = logging.getLogger(__name__)

@shared_task
def convert_to_hls(video_id):
    logger.info(f"Starting HLS conversion for video ID: {video_id}")

    try:
        video = Video.objects.get(id=video_id)
        input_file = video.file.path
        output_dir = os.path.join('media', 'videos', 'hls', str(video.id))
        os.makedirs(output_dir, exist_ok=True)

        # Define variants
        variants = [
            {'scale': '426x240', 'bitrate': '500k', 'variant': '0'},
            {'scale': '640x360', 'bitrate': '1000k', 'variant': '1'},
            {'scale': '1280x720', 'bitrate': '2500k', 'variant': '2'},
            {'scale': '1920x1080', 'bitrate': '5000k', 'variant': '3'}
        ]
        # Generate each variant separately
        for v in variants:
            cmd = [
                'ffmpeg', '-i', input_file,
                '-vf', f'scale={v["scale"]}',
                '-b:v', v['bitrate'], '-c:v', 'h264', '-preset', 'fast',
                '-c:a', 'aac', '-b:a', '128k',
                '-f', 'hls',
                '-hls_time', '10',
                '-hls_list_size', '0',
                '-hls_segment_filename', os.path.join(output_dir, f'segment_{v["variant"]}_%03d.ts'),
                os.path.join(output_dir, f'variant_{v["variant"]}.m3u8')
            ]

            logger.info(f"Running command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)

        # Generate master playlist
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

        # Save master playlist path to the video model
        video.hls_master_playlist = master_playlist
        video.save()
        logger.info(f"Successfully completed HLS conversion for video ID: {video_id}")

    except Exception as e:
        logger.error(f"Error in HLS conversion task: {e}")

@shared_task(queue='default')
def test_celery_task():
    print("Task started!")
    time.sleep(1)
    print("Task completed!")
    return "Task completed"