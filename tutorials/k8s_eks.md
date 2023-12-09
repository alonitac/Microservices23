# AWS Elastic Kubernetes Service (EKS) 

Kubernetes is shipped by [many different distributions](https://nubenetes.com/matrix-table/#), each aimed for a specific purpose.
Throughout this tutorial we will be working with Elastic Kubernetes Service (EKS), which is a Kubernetes cluster managed by AWS.  

## Elastic Kubernetes Service (EKS)

To provision an EKS cluster using the AWS Management Console:

1. Open the Amazon EKS console at https://console.aws.amazon.com/eks/home#/clusters
2. Choose **Add cluster** and then choose **Create**.
3. On the Configure cluster page, enter the following fields:
    - **Name** – A name for your cluster. E.g. `john-k8s`.
    - **Kubernetes version** – we'll be working with k8s `1.28`. 
    - **Cluster service role** – We already created for you a role with appropriate permissions: `eks-role`. The EKS cluster IAM role allows the Kubernetes control plane to manage AWS resources on your behalf.  
    - Leave other default definitions.
4. On the **Specify networking** page, select values for the following fields:
    - **VPC** – Choose an existing default VPC. 
    - **Subnets** – By default, all available subnets in the VPC specified in the previous field are preselected. You must select at least two.
    - **Security groups** - leave empty.
    - For **Cluster endpoint access**, select **Public**.
5. Leave the **Configure observability** page like that.
6. Leave the **Select add-ons** page and the **Configure selected add-ons settings** page like that.
7. On the **Review and create** page, review your  cluster information and create. 

Cluster provisioning takes several minutes.

`kubectl` is a cli tool to control Kubernetes cluster. Install it in your environment by:

```bash 
sudo snap install kubectl --classic
```

You have to set `kubectl` properly in order to authenticate with your EKS cluster. 

To do so, first let's disable a 

To allow access from within your environments:

1. 

Create `kubectl`:

```bash
sudo snap install kubectl --classic
```

Upon successful creation, configure `kubectl` to communicate with your cluster by adding a new context to the `kubeconfig` file.

1. First 

```shell
aws eks --region <region> update-kubeconfig --name <cluster_name>
```

Change `<region>` and `<cluster_name>` accordingly.

## Manage Nodes

A fresh EKS cluster does have the Control Plane server, doesn't have Nodes.

EKS cluster offer different approaches to create and manage Nodes:

1. **EKS managed node groups**: EKS create and manage the cluster EC2 instances for you. Just choose an instance type, minimum and maximum number of Nodes. 
2. **Self-managed nodes**: you manually add EC2 instances to the cluster. You have to create the instances yourself, configure them and connect them to the cluster Control Plane.  
3. **AWS Fargate**: a technology that provides on-demand, right-sized compute capacity without even seeing the EC2 instances. You don't have to provision, configure, or scale groups of virtual machines on your own. Just schedule a Pod and AWS will take control on compute themselves (feels like "serverless" cluster). 

We will use the **EKS manage node groups** approach. 

![](../.img/k8s_eks_nodes.png)

### EKS managed node groups

Managed node groups are a blend of automation and customization for managing a collection of EC2 instances within an EKS cluster.
AWS takes care of tasks like patching, updating, and scaling nodes, easing operational aspects.


<img src="../.img/eks_ng.png" width="60%" />

Amazon EKS provides specialized AMIs that are called [Amazon EKS optimized AMIs](https://docs.aws.amazon.com/eks/latest/userguide/eks-optimized-ami.html).
The AMIs are configured to work with Amazon EKS.


To create a managed node group using the AWS Management Console:

1. Wait for your cluster status to show as `ACTIVE`.
2. Open the Amazon EKS console at https://console.aws.amazon.com/eks/home#/clusters.
3. Choose the name of the cluster that you want to create a managed node group in.
4. Select the **Compute** tab.
5. Choose **Add node group**.
6. On the **Configure node group** page, fill out the parameters accordingly. 
   - **Node IAM role** – Choose the node instance role to use with your node group. [Read here how to do it](https://docs.aws.amazon.com/eks/latest/userguide/create-node-role.html#create-worker-node-role).
   - **Minimum size** - **1**.
   - **Maximum size** - **2**.
7. On the **Set compute and scaling configuration** page, fill out the parameters accordingly:
   - **Instance types** - Choose `t*.large`.
8. Watch the status of your nodes and wait for them to reach the `Ready` status:
  ```bash
  kubectl get nodes --watch
  ```

## Install EBS CSI driver

The [EBS CSI driver](https://github.com/kubernetes-sigs/aws-ebs-csi-driver) allows you to create and manage EBS volumes as storage for the Kubernetes Volumes that you create. 

The Amazon EBS CSI plugin requires IAM permissions to make calls to AWS APIs on your behalf. For more information, see [Creating the Amazon EBS CSI driver IAM role](https://docs.aws.amazon.com/eks/latest/userguide/csi-iam-role.html).

1. Open the Amazon EKS console at https://console.aws.amazon.com/eks/home#/clusters
2. In the left navigation pane, choose **Clusters**.
3. Choose the name of the cluster that you want to configure the Amazon EBS CSI add-on for.
4. Choose the **Add-ons** tab.
5. Choose **Get more add-ons**.
6. On the **Select add-ons** page, do the following:

    - In the **Amazon EKS-addons** section, select the **Amazon EBS CSI Driver** check box.
    - Choose **Next**.
7. On the **Configure selected add-ons settings** page, select the name of an **IAM role** that you attached the Amazon EBS CSI driver IAM policy.
8. On the **Review and add** page, choose **Create**. 

## Provision the Online Boutique service

Let's deploy the Online Boutique service

```bash 
kubectl apply -f k8s/online-boutique/release-0.8.0.yaml
```

## Nodes Autoscaling 

So far, we've seen Pod horizontal autoscaling (HPA). 
But Kubernetes clusters have actually two levels of scaling - Pod level scaling (done using HPA), and Node level scaling. 

Amazon EKS supports two Node level autoscaling products:

1. [Karpenter](https://karpenter.sh/): Karpenter is a flexible, high-performance Kubernetes cluster autoscaler (see exercise below).
2. [Cluster Autoscaler](https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/aws/README.md):  automatically adjusts the number of nodes using Auto Scaling groups.

## Cleanup your experimental clusters

> [!IMPORTANT]
> When you're done with experimenting provisioning of EKS cluster, please delete your cluster and node groups. 

## Working on `k8s-main` - our shared Kubernetes cluster 

### Create your own namespace in the shared cluster

In order our group to share a single EKS cluster peacefully, each one of you can work on **different k8s namespace**. 

**Kubernetes Namespaces** provide a way to logically partition and isolate resources within a cluster, allowing for better organization, access control, and resource management.
Create your own namespace in k8s:

```bash
kubectl create ns <your-ns-alias>
```

It's recommended to set `kubectl` to work by default against your namespace:

```bash
kubectl config set-context --current --namespace=<your-ns-alias>
```

### Enabling IAM principal access to your cluster

When you create an EKS cluster, the IAM user that creates the cluster is automatically granted a admin on the cluster.
Other IAM principals (users, roles) doesn't have access to the cluster. 

Follow the below docs to allow other IAM users and roles to access the cluster: 

https://docs.aws.amazon.com/eks/latest/userguide/add-user-role.html

# Exercise 

### :pencil2: Karpenter

Karpenter is a flexible, high-performance Kubernetes cluster autoscaler that helps improve application availability and cluster efficiency. 
Karpenter launches right-sized compute resources in response to changing application load. This option can provision just-in-time compute resources that meet the requirements of your workload.

Follow the getting started guide: 

https://karpenter.sh/docs/getting-started/getting-started-with-karpenter/


### :pencil2: Add IAM user or role to your EKS cluster

When you create an Amazon EKS cluster, the IAM principal that creates the cluster is automatically granted system:masters permissions

To grant additional IAM principals the ability to interact with your cluster, edit the aws-auth ConfigMap within Kubernetes

### :pencil2: Pod identity

EKS Pod Identities provide the ability to manage credentials for your applications, similar to the way that Amazon EC2 instance profiles provide credentials to Amazon EC2 instances. Instead of creating and distributing your AWS credentials to the containers or using the Amazon EC2 instance's role, you associate an IAM role with a Kubernetes service account and configure your Pods to use the service account.

https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html

### S3 CSI driver 

https://docs.aws.amazon.com/eks/latest/userguide/s3-csi.html


### CSI snapshot controller 

https://docs.aws.amazon.com/eks/latest/userguide/csi-snapshot-controller.html

### kyverno 

https://github.com/nirmata/kyverno-notation-aws

