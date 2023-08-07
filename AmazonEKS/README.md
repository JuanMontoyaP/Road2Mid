# Deploying a containerized App with Amazon EKS

1. Creating the Amazon EKS cluster
```
eksctl create cluster \
--name eks-lab-cluster \
--nodegroup-name worknodes-1 \
--node-type t3.medium \
--nodes 2 \
--nodes-min 1 \
--nodes-max 4 \
--managed \
--region ${AWS_DEFAULT_REGION}
```

The command creates an Amazon EKS Cluster that includes an Amazon EKS control plane and two worker nodes that the control plane manages.

2. Creating Docker images

```
docker build -t website .
docker build -t sidecar .
```

3. Creating an Amazon ECR repository and pushing the Docker image to it

```
aws ecr create-repository \
 --repository-name website \
 --region ${AWS_DEFAULT_REGION}
aws ecr create-repository \
 --repository-name sidecar \
 --region ${AWS_DEFAULT_REGION}
```

Set environmental variables to set to those repos:
```
cd ~/environment/eksLabRepo/
export ACCOUNT_NUMBER=$(aws sts get-caller-identity \
 --query 'Account' \
 --output text)
export ECR_REPO_URI_WEBSITE=$(aws ecr describe-repositories \
 --repository-names website \
 --region ${AWS_DEFAULT_REGION} \
 --query 'repositories[*].repositoryUri' \
 --output text)
export ECR_REPO_URI_SIDECAR=$(aws ecr describe-repositories \
 --repository-names sidecar \
 --region ${AWS_DEFAULT_REGION} \
 --query 'repositories[*].repositoryUri' \
 --output text)
```

Push the images to ECR
```
docker tag website:latest $ECR_REPO_URI_WEBSITE:latest
docker push $ECR_REPO_URI_WEBSITE:latest
docker tag sidecar:latest $ECR_REPO_URI_SIDECAR:latest
docker push $ECR_REPO_URI_SIDECAR:latest
```

4. Checking EKS cluster.

```
aws eks describe-cluster \
 --name eks-lab-cluster \
 --query 'cluster.status' \
 --output text
```

```
kubectl get svc
```

5. Running the AWS Load Balancer Controller on Amazon EKS

```
sh ./albController.sh
```

```
kubectl get pods \
 -n kube-system \
 --selector=app.kubernetes.io/name=aws-load-balancer-controller
```

6. Deploying the lab application

```
kubectl create namespace containers-lab

envsubst < k8s-all.yaml | kubectl apply -f -

kubectl get all -n containers-lab

kubectl get pods -n containers-lab

kubectl get ingress -n containers-lab
```

7. Configuring IAM roles for EKS

```
eksctl create iamserviceaccount \
    --name iampolicy-sa \
    --namespace containers-lab \
    --cluster eks-lab-cluster \
    --role-name "eksRole4serviceaccount" \
    --attach-policy-arn arn:aws:iam::$ACCOUNT_NUMBER:policy/eks-lab-read-policy \
    --approve \
    --override-existing-serviceaccounts


kubectl get sa iampolicy-sa -n containers-lab -o yaml

kubectl set serviceaccount \
 deployment eks-lab-deploy \
 iampolicy-sa -n containers-lab

kubectl describe deployment.apps/eks-lab-deploy \
 -n containers-lab | grep 'Service Account'

kubectl get ingress -n containers-lab
```

8. Deploying Amazon CloudWatch container insights service

```
aws ec2 describe-instances --filters Name=instance-type,Values=t3.medium --query 'Reservations[*].Instances[*].{Instance:InstanceId,AZ:Placement.AvailabilityZone,Name:Tags[?Key==`Name`]|[0].Value}' --output table


export instanceProfileArn=$(aws ec2 describe-instances \
 --instance-ids $instanceId \
 --query 'Reservations[*].Instances[*].IamInstanceProfile.Arn' \
 --output text)
export instanceProfileName=$(echo $instanceProfileArn | \
 awk -F/ '{print $NF}')
export roleName=$(aws iam get-instance-profile \
 --instance-profile-name $instanceProfileName \
 --query "InstanceProfile.Roles[*].RoleName" \
 --output text)
aws iam attach-role-policy \
 --role-name $roleName \
 --policy-arn arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy


export CLUSTER_NAME=$(aws eks describe-cluster \
 --name eks-lab-cluster \
 --query 'cluster.name' \
 --output text)
curl https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/latest/k8s-deployment-manifest-templates/deployment-mode/daemonset/container-insights-monitoring/quickstart/cwagent-fluentd-quickstart.yaml | \
 sed "s/{{cluster_name}}/$CLUSTER_NAME/;s/{{region_name}}/$AWS_DEFAULT_REGION/" | \
 kubectl apply -f -

```
