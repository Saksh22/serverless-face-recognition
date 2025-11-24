#Project 2 Part 2
import os
import subprocess
import math
import boto3
import json


s3 = boto3.client('s3')
client = boto3.client('lambda')

def video_splitting_cmdline(video_filename):
    filename = os.path.basename(video_filename)
    outfile = os.path.splitext(filename)[0] + ".jpg"

    split_cmd = '/opt/ffmpeg-layer/ffmpeg -i ' + '/tmp/' + video_filename + ' -vframes 1 ' + '/tmp/' + outfile
    try:
        subprocess.check_call(split_cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(e.returncode)
        print(e.output)

    fps_cmd = '/opt/ffmpeg-layer/ffmpeg -i ' + '/tmp/' + video_filename + ' 2>&1 | sed -n "s/.*, \\(.*\\) fp.*/\\1/p"'
    fps = subprocess.check_output(fps_cmd, shell=True).decode("utf-8").rstrip("\n")
    return outfile
    
def lambda_handler(event,context):
    input_bucket_name = event['Records'][0]['s3']['bucket']['name']
    video_filename = event['Records'][0]['s3']['object']['key']
    stage_bucket_name = "1229499923-stage-1"
    
    s3.download_file(input_bucket_name, video_filename, f'/tmp/{video_filename}')
    
    output_key = video_splitting_cmdline(video_filename)
    # print(output_key)
    
    payload = {"bucket": stage_bucket_name, "key": output_key}
    # print(payload)
        
    with open('/tmp/' + output_key, 'rb') as data:
        s3.put_object(Bucket=stage_bucket_name, Key=output_key, Body=data)
        
    response = client.invoke(
        FunctionName='arn:aws:lambda:us-east-1:851725184454:function:face-recognition',
        InvocationType='Event',
        Payload=json.dumps({
                'bucket_name': stage_bucket_name,
                'image_file_name': output_key
            })
        )
        
    print(response)
        
    return {
        'statusCode': 200,
        'body': 'Successfully processed and uploaded frames to stage bucket.'
    }
