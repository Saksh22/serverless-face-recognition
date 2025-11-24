#__copyright__   = "Copyright 2024, VISA Lab"
#__license__     = "MIT"

__copyright__   = "Copyright 2024, VISA Lab"
__license__     = "MIT"

import os
import cv2
import boto3
from PIL import Image, ImageDraw, ImageFont
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
import os

print("running.........")

os.environ['TORCH_HOME'] = '/tmp/models/'

def list_env_variables():
    for key, value in os.environ.items():
        print(f"{key}: {value}")


list_env_variables()
mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20) # initializing mtcnn for face detection
resnet = InceptionResnetV1(pretrained='vggface2').eval() # initializing resnet for face img to embeding conversion
s3 = boto3.client('s3')

def handler(event,context):
 
    input_bucket_name = event['bucket_name']
    image_filename = event['image_file_name'] #test_00.jpg
    output_bucket_name = "1229499923-output"
    download_path = f'/tmp/{image_filename}'
    print(input_bucket_name, image_filename, output_bucket_name , download_path)
    s3.download_file(input_bucket_name, image_filename, download_path)
    
    output_key = face_recognition_function(download_path)
    print("Face recognition hogaya", output_key)
        
    with open('/tmp/' + output_key, 'rb') as data:
        s3.put_object(Bucket=output_bucket_name, Key=output_key, Body=data)
        
    return {
        'statusCode': 200,
        'body': 'Successfully processed and uploaded frames to stage bucket.'
    }


def face_recognition_function(key_path):
    # Face extraction
    img = cv2.imread(key_path, cv2.IMREAD_COLOR)
    boxes, _ = mtcnn.detect(img)

    # Face recognition
    key = os.path.splitext(os.path.basename(key_path))[0].split(".")[0]
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    face, prob = mtcnn(img, return_prob=True, save_path=None)
    s3.download_file('1229499923-in-bucket','data.pt','/tmp/data.pt') # loading data.pt file
    saved_data = torch.load('/tmp/data.pt')
    print(saved_data[0])
    if face != None:
        emb = resnet(face.unsqueeze(0)).detach()  # detech is to make required gradient false
        embedding_list = saved_data[0]  # getting embedding data
        name_list = saved_data[1]  # getting list of names
        dist_list = []  # list of matched distances, minimum distance is used to identify the person
        for idx, emb_db in enumerate(embedding_list):
            dist = torch.dist(emb, emb_db).item()
            dist_list.append(dist)
        idx_min = dist_list.index(min(dist_list))

        # Save the result name in a file
        with open("/tmp/" + key + ".txt", 'w+') as f:
            f.write(name_list[idx_min])
        return key + ".txt"
    else:
        print(f"No face is detected")
    return



