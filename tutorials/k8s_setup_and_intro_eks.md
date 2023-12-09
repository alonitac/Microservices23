# Kubernetes setup and introduction

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

## Controlling the cluster

`kubectl` is a cli tool to control Kubernetes cluster. Install it in your IDE environment by:

```bash 
sudo snap install kubectl --classic
```

Now let's authenticate `kubectl` with your EKS cluster. 

To do so, you have to generate an access token for your AWS user and configure your IDE environment to use this credentials:

1. By default, your IDE environment uses a temporary credentials feature which changes from time to time. Disable it by:
   - Click on the **Settings** icon in the top right corner of you IDE (or click `CTRL+,`).
   - Under **AWS Settings** -> **Credentials**, disable the **AWS managed temporary credentials** toogle. 
2. Generate the access token:

```bash
aws iam create-access-key --user-name YOUR_AWS_USERNAME
```

Change `YOUR_AWS_USERNAME` to your user.

3. Let's configure the generated creds in your IDE environment. Click on the "AWS" logo in the left vertical menu. 
4. In the opened navigation pane, right-click on the current connection under **Explorer**, and click **Add new connection**.
5. Choose **Use IAM Credentials**.
6. Insert your Access Key (this is the `AccessKeyId` field in the generated access token) and click **Enter**.
7. Insert your Secret Key (this is the `SecretAccessKey` field in the generated access token), click **Enter**.

Now you should be able to configure `kubectl` to communicate with your cluster by adding a new context to the `kubeconfig` file:

```shell
aws eks --region us-east-1 update-kubeconfig --name <cluster_name>
```

Change `<cluster_name>` accordingly. 

Make sure `kubectl` successfully communicates with your cluster:

```console
$ kubectl get pods -A
NAMESPACE     NAME                      READY   STATUS    RESTARTS   AGE
kube-system   coredns-58488c5db-g89gc   0/1     Pending   0          152m
kube-system   coredns-58488c5db-z4f67   0/1     Pending   0          152m
```

## Manage Nodes

A fresh EKS cluster doesn't have Nodes, but only the Control Plane server.

EKS cluster offer different approaches to create and manage Nodes:

1. **EKS managed node groups**: EKS create and manage the cluster EC2 instances for you. Just choose an instance type, minimum and maximum number of Nodes. 
2. **Self-managed nodes**: you manually add EC2 instances to the cluster. You have to create the instances yourself, configure them and connect them to the cluster Control Plane.  
3. **AWS Fargate**: a technology that provides on-demand, right-sized compute capacity without even seeing the EC2 instances. You don't have to provision, configure, or scale groups of virtual machines on your own. Just schedule a Pod and AWS will take control on compute themselves (feels like "serverless" cluster). 

We will use the **EKS manage node groups** approach.  

<img src="../.img/eks_ng.png" width="60%" />

To create a managed node group using the AWS Management Console:

1. Wait for your cluster status to show as `ACTIVE`.
2. Open the Amazon EKS console at https://console.aws.amazon.com/eks/home#/clusters.
3. Choose the name of the cluster that you want to create a managed node group in.
4. Select the **Compute** tab.
5. Choose **Add node group**.
6. On the **Configure node group** page, fill out the parameters accordingly. 
   - **Name** - To your choice. E.g. `default-ng`.
   - **Node IAM role** – Choose the `k8s-ng-role` (this role was created for your node groups in advanced).
7. On the **Set compute and scaling configuration** page, keep all the default configurations.
8. On the **Specify networking** page, keep all the default configurations.
9. Review and create.
    
## Install k8s dashboard 

The [k8s dashboard](https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/) is a web-based user interface.
You can use the dashboard to troubleshoot your application, and manage the cluster resources.

To install the dashboard, perform:

```bash
cd ~/environment/Microservices23
kubectl apply -f k8s/k8s-dashboard.yaml
```

By default, applications deployed in k8s cluster are not accessible from outside the cluster.
To access the dashboard app you can use the `kubectl port-forward` command.
This is a method used to access and interact with internal resources of the cluster from your local machine:

```bash
kubectl port-forward service/kubernetes-dashboard 8081:8081 -n kubernetes-dashboard --address 0.0.0.0
```

This command occupies the terminal, allowing you to access the dashboard from your local machine.

Open the web browser and type:

```text
http://YOUR_INSTANCE_PUBLIC_DNS:8081
```

While `YOUR_INSTANCE_PUBLIC_DNS` is your public DNS name.

In the dashboard authentication page, click **Skip**.

## Deploy applications in the cluster

Let's see Kubernetes cluster in all his glory! 

[Online Boutique](https://github.com/GoogleCloudPlatform/microservices-demo) is a microservices demo application, consists of an 11-tier microservices.
The application is a web-based e-commerce app where users can browse items, add them to the cart, and purchase them.

Here is the app architecture and description of each microservice:

<img src="../.img/k8s_online-boutique-arch.png" width="80%">


| Service                                              | Language      | Description                                                                                                                       |
| ---------------------------------------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| frontend                           | Go            | Exposes an HTTP server to serve the website. Does not require signup/login and generates session IDs for all users automatically. |
| cartservice                     | C#            | Stores the items in the user's shopping cart in Redis and retrieves it.                                                           |
| productcatalogservice | Go            | Provides the list of products from a JSON file and ability to search products and get individual products.                        |
| currencyservice             | Node.js       | Converts one money amount to another currency. Uses real values fetched from European Central Bank. It's the highest QPS service. |
| paymentservice               | Node.js       | Charges the given credit card info (mock) with the given amount and returns a transaction ID.                                     |
| shippingservice             | Go            | Gives shipping cost estimates based on the shopping cart. Ships items to the given address (mock)                                 |
| emailservice                   | Python        | Sends users an order confirmation email (mock).                                                                                   |
| checkoutservice             | Go            | Retrieves user cart, prepares order and orchestrates the payment, shipping and the email notification.                            |
| recommendationservice | Python        | Recommends other products based on what's given in the cart.                                                                      |
| adservice                         | Java          | Provides text ads based on given context words.                                                                                   |
| loadgenerator                 | Python/Locust | Continuously sends requests imitating realistic user shopping flows to the frontend.                                              |


To deploy the app in you cluster, perform the below command from the root directory of your shared repo (make sure the YAML file exists): 

```bash 
kubectl apply -f k8s/online-boutique/release-0.8.0.yaml
```

By default, applications running within the cluster are not accessible from outside the cluster.
There are various techniques available to enable external access, we will cover some of them later on.

Using port forwarding allows developers to establish a temporary tunnel for debugging purposes and access applications running inside the cluster from their local machines.

```bash
kubectl port-forward svc/frontend 8080:80 --address 0.0.0.0
```

Visit the app.


## More information about Kubernetes API server and the `kubectl` cli

The core of Kubernetes' control plane is the **API server**. The API server exposes an HTTP API that lets you communicate with the cluster, and let k8s components communicate with one another.

Usually you don't communicate with the API server directly, but using `kubectl`, which internally communicates with the API server on your behalf.

For example, to list your Pods:

```console
$ kubectl get pods
NAME                               READY   STATUS    RESTARTS   AGE
flask-deployment-7f6549f7b6-6lm9k  1/1     Running   0          2m
```

The above output shows only the running Pods in the `default` namespace. 
In Kubernetes, **namespaces** provides a mechanism for isolating groups of resources within a single cluster.

To list Pods from all namespaces:

```console
$ kubectl get pods --all-namespaces
NAMESPACE              NAME                                         READY   STATUS    RESTARTS      AGE
kube-system            coredns-5d78c9869d-rdzzt                     1/1     Running   2 (9h ago)    10h
kube-system            etcd-minikube                                1/1     Running   2 (9h ago)    10h
kube-system            kube-apiserver-minikube                      1/1     Running   2 (9h ago)    10h
kube-system            kube-controller-manager-minikube             1/1     Running   2 (9h ago)    10h
kube-system            kube-proxy-cs4mq                             1/1     Running   2 (9h ago)    10h
kube-system            kube-scheduler-minikube                      1/1     Running   2 (9h ago)    10h
kube-system            storage-provisioner                          1/1     Running   5 (26m ago)   10h
kubernetes-dashboard   dashboard-metrics-scraper-5dd9cbfd69-64kvk   1/1     Running   2 (9h ago)    10h
kubernetes-dashboard   kubernetes-dashboard-5c5cfc8747-9wsj6        1/1     Running   3 (9h ago)    10h
```

`kubectl` can communicate with multiple existed k8s clusters. To change the cluster with which `kubectl` is communicating:

```console 
$ kubectl config use-context my-production-cluster
Switched to context "my-production-cluster".

$ kubectl config use-context my-dev-cluster
Switched to context "my-dev-cluster".
```

### Organizing cluster access using kubeconfig files

How `kubectl` "knows" our EKS cluster? 

`kubectl` uses **kubeconfig file** to find the information it needs to choose a cluster and communicate with the API server of a cluster.

By default, `kubectl` looks for a file named `config` in the `$HOME/.kube` directory. 
Let's take a look on your `~/.kube/config`. The three main entries are `users`, `clusters` and `contexts`. 

- `users` are identities, defined by certificate and key. 
- `clusters` defines certain cluster information that you may want to interact with. Each entry under clusters typically includes the cluster name, the cluster's API server URL, and the CA certificate used to verify the authenticity of the cluster's API server certificate.
- A `context` is used to group access information under a convenient name. Each context has three parameters: `cluster`, `namespace`, and `user`, which basically says: "Use the credentials of the user X to access the Y namespace of the Z cluster".

