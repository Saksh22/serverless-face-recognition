# Video Processing & Face Recognition Pipeline

A serverless AWS Lambda-based application for processing videos and performing face recognition using deep learning models.

## Overview

This project implements a two-stage pipeline that:
1. **Video Splitting**: Extracts frames from video files using FFmpeg
2. **Face Recognition**: Performs face detection and recognition on extracted frames using facenet_pytorch

The application is designed to run on AWS Lambda with S3 bucket integration for input/output handling.

## Project Structure

```
├── handler.py              # Face recognition Lambda handler
├── videosplitting.py       # Video splitting and extraction Lambda handler
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration for Lambda deployment
└── README.md              # Project documentation
```

## Features

- **Video Frame Extraction**: Automatically extracts frames from video files
- **Face Detection**: Uses MTCNN (Multi-task Cascaded Convolutional Networks) for robust face detection
- **Face Recognition**: Leverages InceptionResnetV1 pretrained on VGGFace2 for face embeddings
- **AWS S3 Integration**: Seamless integration with S3 buckets for input/output
- **AWS Lambda Support**: Containerized for deployment as AWS Lambda functions
- **Automated Pipeline**: Lambda functions trigger each other to create a complete workflow

## Architecture

### Video Splitting Handler (`videosplitting.py`)
- Triggered by S3 video uploads
- Extracts first frame from video using FFmpeg
- Uploads frame to stage bucket
- Invokes face recognition Lambda function

### Face Recognition Handler (`handler.py`)
- Receives frame from video splitting stage
- Detects faces in the image
- Generates face embeddings
- Outputs results to output bucket

## Dependencies

- **PyTorch**: Deep learning framework
- **facenet_pytorch**: Face detection and recognition models
- **OpenCV**: Computer vision processing
- **Pillow**: Image manipulation
- **boto3**: AWS SDK for Python
- **FFmpeg**: Video processing (deployed as Lambda layer)

See `requirements.txt` for complete dependency list.

## Installation & Setup

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### AWS Deployment

1. **Build Docker image**
   ```bash
   docker build -t video-processing:latest .
   ```

2. **Create Lambda function from Docker image**
   - Push Docker image to ECR
   - Create Lambda function using container image
   - Configure S3 event triggers

3. **Set up S3 buckets**
   - Input bucket for video files
   - Stage bucket for extracted frames
   - Output bucket for processed results

4. **Configure IAM permissions**
   - Allow Lambda to read from input/stage buckets
   - Allow Lambda to write to stage/output buckets
   - Allow Lambda to invoke other Lambda functions

## Configuration

### Environment Variables

- `TORCH_HOME`: Set to `/tmp/models/` for Lambda (for model caching)

### S3 Bucket Names

- **Input Bucket**: Source for video files
- **Stage Bucket**: `1229499923-stage-1` (for intermediate frames)
- **Output Bucket**: `1229499923-output` (for final results)

## Usage

### Triggering the Pipeline

1. Upload a video file to the input S3 bucket
2. The video splitting Lambda function is automatically triggered
3. A frame is extracted and uploaded to the stage bucket
4. Face recognition Lambda is invoked automatically
5. Results are saved to the output bucket

### Lambda Event Format

**Video Splitting Handler**
```json
{
  "Records": [{
    "s3": {
      "bucket": { "name": "input-bucket" },
      "object": { "key": "video-filename.mp4" }
    }
  }]
}
```

**Face Recognition Handler**
```json
{
  "bucket_name": "stage-bucket",
  "image_file_name": "extracted-frame.jpg"
}
```

## Development

### Requirements

- Python 3.8+
- Docker (for containerized deployment)
- AWS CLI (for deployment)
- FFmpeg Lambda layer (required for video splitting)

### File Descriptions

| File | Purpose |
|------|---------|
| `handler.py` | Face recognition Lambda function with MTCNN and ResNet models |
| `videosplitting.py` | Video frame extraction and stage management |
| `requirements.txt` | Python package dependencies |
| `Dockerfile` | Lambda container image definition |

## License

Copyright 2024, VISA Lab
Licensed under the MIT License

## Notes

- Models are cached in `/tmp/models/` to improve Lambda execution times
- The pipeline uses S3 for temporary file storage during processing
- Face detection and recognition models require significant memory; ensure Lambda has adequate resource allocation
- FFmpeg must be available as a Lambda layer for video processing

## Troubleshooting

- **Model loading errors**: Ensure TORCH_HOME is set to `/tmp/models/` and Lambda has sufficient memory
- **S3 access errors**: Verify IAM roles and bucket permissions
- **FFmpeg not found**: Check that FFmpeg Lambda layer is properly attached
- **Lambda timeout**: Increase timeout and memory allocation in Lambda configuration

## Future Enhancements

- Support for multiple face detection models
- Batch processing capabilities
- Custom model fine-tuning
- Real-time processing pipeline
- Web interface for results visualization
