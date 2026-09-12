# AWS ECS Fargate Deployment Guide

This guide details the manual steps required to set up the foundational infrastructure on AWS Elastic Container Service (ECS) before GitHub Actions can automatically deploy to it.

Because the GitHub Action `amazon-ecs-deploy-task-definition` updates an *existing* ECS Service, you must create the Cluster, a placeholder Task Definition, and the Service manually the first time.

## Step 1: Create the ECS Cluster
1. Log in to your **AWS Management Console** and make sure you are in your desired region (e.g., **`us-east-1` (N. Virginia)**) (check the top right corner).
2. Search for **ECS** (Elastic Container Service) and open it.
3. Click on **Clusters** in the left sidebar, then click the **Create cluster** button.
4. **Cluster name**: Type exactly `document-portal-cluster-dev`
5. **Infrastructure**: Check **AWS Fargate (serverless)**.
6. Click **Create** and wait a moment for it to provision.

## Step 2: Create a Placeholder Task Definition
*You must create a temporary task definition so you can create the service. GitHub Actions will overwrite this with the real one later.*
1. In the left sidebar of ECS, click **Task definitions**, then click **Create new task definition** -> **Create new task definition**.
2. **Task definition family**: Type `document-portal-dev`
3. **Infrastructure requirements**: Select **AWS Fargate**.
4. **Operating system/Architecture**: Linux/X86_64
5. **Task size**: Set CPU to `.25 vCPU` and Memory to `0.5 GB`.
6. **Task roles**: Ensure **Task execution role** is set to `ecsTaskExecutionRole` (and Task Role if prompted).
7. **Container - 1**:
   - **Name**: `document-portal-container`
   - **Image URI**: Type `nginx:latest` *(This is a placeholder image; GitHub Actions will overwrite it with your actual ECR image).*
   - **Container port**: `8000` (Protocol: TCP).
8. Scroll to the bottom and click **Create**.

## Step 3: Create the ECS Service
1. Go back to **Clusters** on the left menu and click on your newly created `document-portal-cluster-dev`.
2. In the **Services** tab (at the bottom), click **Create**.
3. **Compute options**: Select **Launch type** and choose **FARGATE**.
4. **Deployment configuration**:
   - **Application type**: Service
   - **Family**: Select `document-portal-dev` (the task definition you just created).
   - **Service name**: Type exactly `document-portal-service-dev`
   - **Desired tasks**: `1`
5. **Networking**: 
   - Choose your default VPC and Subnets.
   - **Security group**: Create a new security group. Under Inbound rules, allow **Custom TCP** on port **8000** from **Anywhere (0.0.0.0/0)** so you can access your web portal.
   - **Public IP**: Ensure this is turned **ON**.
6. Scroll to the bottom and click **Create**.

## Next Steps
Once the Service is successfully created and reaches a steady state in your cluster, go back to GitHub and re-run your failed GitHub Actions workflow. The CI/CD pipeline will automatically find the cluster and service, replace the placeholder `nginx` image with your actual application image, and deploy it smoothly!
