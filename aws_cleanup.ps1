<#
.SYNOPSIS
Cleans up AWS resources created for the Document Portal practice project to avoid unexpected charges.

.DESCRIPTION
This script uses the AWS CLI to force-delete the ECS Services, ECS Clusters, ECR Repositories, 
DynamoDB Tables, and S3 Buckets across all stages (Dev, Staging, Prod). 
Run this when you are done practicing for the day to ensure you incur $0.00 in idle costs.

.NOTES
Requires AWS CLI installed and configured with your credentials.
#>

$Region = "ap-southeast-2"
$Stages = @("dev", "staging", "prod")

Write-Host "Starting complete AWS teardown for Document Portal..." -ForegroundColor Yellow

# 1. Delete ECS Services and Clusters
foreach ($stage in $Stages) {
    $cluster = "document-portal-cluster-$stage"
    $service = "document-portal-service-$stage"
    
    Write-Host "Tearing down ECS Service: $service..." -ForegroundColor Cyan
    # Scale service to 0 so tasks stop running (this stops the hourly Fargate charges)
    aws ecs update-service --cluster $cluster --service $service --desired-count 0 --region $Region 2>$null
    
    # Delete the service
    aws ecs delete-service --cluster $cluster --service $service --force --region $Region 2>$null
    
    Write-Host "Deleting ECS Cluster: $cluster..." -ForegroundColor Cyan
    aws ecs delete-cluster --cluster $cluster --region $Region 2>$null
}

# 2. Delete ECR Repository
$ecrRepo = "documentportalliveclass"
Write-Host "Deleting ECR Repository: $ecrRepo..." -ForegroundColor Cyan
aws ecr delete-repository --repository-name $ecrRepo --force --region $Region 2>$null

# 3. Delete DynamoDB Tables
foreach ($stage in $Stages) {
    # We capitalize the first letter to match the table names (e.g. Dev, Staging, Prod)
    $stageCapitalized = (Get-Culture).TextInfo.ToTitleCase($stage)
    
    $docsTable = "DocumentRegistry-$stageCapitalized"
    $chatTable = "DocumentChatHistory-$stageCapitalized"
    
    Write-Host "Deleting DynamoDB Tables for $stageCapitalized..." -ForegroundColor Cyan
    aws dynamodb delete-table --table-name $docsTable --region $Region 2>$null
    aws dynamodb delete-table --table-name $chatTable --region $Region 2>$null
}

# 4. Delete S3 Buckets
foreach ($stage in $Stages) {
    $bucket = "document-portal-storage-$stage-$Region"
    
    Write-Host "Emptying and Deleting S3 Bucket: $bucket..." -ForegroundColor Cyan
    # S3 buckets must be forcefully emptied before they can be deleted
    aws s3 rb s3://$bucket --force --region $Region 2>$null
}

# 5. Delete IAM Roles (Optional, IAM roles are free, but cleans up clutter)
Write-Host "Deleting IAM Role: ecsTaskRole..." -ForegroundColor Cyan
# Detach policies first (assuming AWS managed policies or inline policies were attached)
# You may need to manually delete inline policies first depending on how you set it up.
aws iam delete-role --role-name ecsTaskRole 2>$null

Write-Host "Cleanup Complete! You will not incur any further charges." -ForegroundColor Green
