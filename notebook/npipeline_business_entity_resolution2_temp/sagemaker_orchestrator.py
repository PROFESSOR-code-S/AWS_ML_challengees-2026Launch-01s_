'''
This is the Python script that leverages the
sagemaker.processing.ScriptProcessor SDK to spin up an isolated compute node
and mounts our raw S3 bucket prefixes in FastFile mode.

'''

'''
This file has one job: It tells AWS to spin up a heavy, powerful server instance,
link it to our S3 bucket using FastFile mode, run our heavy training logic,
save the results, and shut down instantly

'''
import os
import boto3
import sagemaker
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput

def launch_sagemaker_scaling_job():
    print("=======================================================================")
    print("INITIALIZING AWS SAGEMAKER SCALING ORCHESTRATOR")
    print("=======================================================================")
    
    # 1. Establish session configurations & security execution roles natively
    sagemaker_session = sagemaker.Session()
    role = sagemaker.get_execution_role()
    region = sagemaker_session.boto_region_name
    
    # 2. Configure your specific S3 structural infrastructure pathways
    # CHANGE THIS to your globally unique S3 bucket name created in the terminal
    bucket_name = "amazon-ml-challenge-2026-team-unique-id" 
    
    s3_input_uri = f"s3://{bucket_name}/raw-data/"
    s3_output_uri = f"s3://{bucket_name}/candidates/"
    
    print(f"-> Target AWS Storage Domain Region: {region}")
    print(f"-> Input Data Stream Prefix:        {s3_input_uri}")
    print(f"-> Output Candidate Destination:     {s3_output_uri}")
    
    # 3. Retrieve the optimized, native AWS Scikit-Learn Framework Container
    # Using the built-in image avoids ECR storage fees and minimizes container build times!
    print("-> Fetching native framework container image URI...")
    container_image_uri = sagemaker.image_uris.retrieve(
        framework="scikit-learn",
        region=region,
        version="1.2-1"
    )
    
    # 4. Provision the isolated, heavy compute processing instance
    # Allocates up to 50 GB of free ephemeral storage that self-destructs post-run
    print("-> Provisioning isolated compute node configuration parameters...")
    processor = ScriptProcessor(
        role=role,
        image_uri=container_image_uri,
        command=["python3"],
        instance_count=1,
        instance_type="ml.m5.xlarge",  # Cost-efficient, high-throughput Free-Tier hours machine
        volume_size_in_gb=50           # Ephemeral workspace scratch space allocation bounds
    )
    
    print("-> Triggering remote execution job sequence...")
    # 5. Execute the orchestration loop and connect the streaming network pipes
    processor.run(
        # Points directly to your local file location layout path inside the repository
        code="../../Package/code/business_entity_resolution/src/blocking_pipeline.py",
        
        inputs=[
            ProcessingInput(
                source=s3_input_uri,
                destination="/opt/ml/processing/input",
                input_mode="FastFile"  # CRUCIAL: Exposes S3 as POSIX mount to stream data on demand
            )
        ],
        outputs=[
            ProcessingOutput(
                source="/opt/ml/processing/output",
                destination=s3_output_uri,
                output_name="candidate_pairs"
            )
        ]
    )
    
    print("=======================================================================")
    print("✅ JOB COMPLETE: Heavy Cloud Scaling Run Concluded Successfully")
    print("=======================================================================")

if __name__ == "__main__":
    launch_sagemaker_scaling_job()