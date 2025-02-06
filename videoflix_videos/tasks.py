from celery import shared_task
import subprocess
from videoflix_videos.models import Video
import os
import time

@shared_task
def convert_to_hls(video_id):
    video = Video.objects.get(id=video_id)
    input_file = video.file.path
    output_dir = os.path.join('media', 'videos', 'hls', str(video.id))
    os.makedirs(output_dir, exist_ok=True)
    
    hls_playlist = os.path.join(output_dir, 'master.m3u8')
    
    ffmpeg_command = [
        'ffmpeg',
        '-i', input_file,
        '-filter_complex',
        '[0:v]split=4[v1][v2][v3][v4];' 
        '[v1]scale=w=426:h=240[v1out];'
        '[v2]scale=w=640:h=360[v2out];'
        '[v3]scale=w=1280:h=720[v3out];'
        '[v4]scale=w=1920:h=1080[v4out]',
        '-map', '[v1out]', '-c:v:0', 'h264', '-b:v:0', '500k',
        '-map', '[v2out]', '-c:v:1', 'h264', '-b:v:1', '1000k',
        '-map', '[v3out]', '-c:v:2', 'h264', '-b:v:2', '2500k',
        '-map', '[v4out]', '-c:v:3', 'h264', '-b:v:3', '5000k',
        '-map', '0:a?', '-c:a', 'aac',
        '-f', 'hls',
        '-hls_time', '10',
        '-hls_list_size', '0',
        '-hls_segment_filename', os.path.join(output_dir, 'segment_%03d.ts'),
        hls_playlist
    ]

    subprocess.run(ffmpeg_command, check=True)
    video.hls_master_playlist = hls_playlist
    video.save()

@shared_task(queue='default')
def test_celery_task():
    print("Task started!")
    time.sleep(100)
    print("Task completed!")
    return "Task completed"