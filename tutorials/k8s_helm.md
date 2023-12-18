# Helm - the Kubernetes Package Manager

## Motivation

**Helm** is a "package manager" for Kubernetes, here are some of the main features of the tool:

- **Helm Charts**: Instead of dealing with numerous YAML manifests, which can be a complex task, Helm introduces the concept of a "Package" (known as **Chart**) – a cohesive group of related YAML manifests that collectively define a single application within the cluster.
  For example, an application might consist of a Deployment, Service, HorizontalPodAutoscaler, ConfigMap, and Secret. 
  These manifests are interdependent and essential for the seamless functioning of the application. 
  Helm encapsulates this collection, making it easier to manage, version, and deploy as a unit.

- **Sharing Charts**: Helm allows you to share your charts, or use other's charts. Want to deploy MongoDB server on your cluster? Someone already done it before, you can use her Helm Chart to with your own configuration values to deploy the MongoDB.  

- **Dynamic manifests**: Helm allows you to create reusable templates with placeholders for configuration values. For example:
  ```yaml
  apiVersion: v1
  kind: Service
  metadata:
    name: {{ .Values.serviceName }}   # the service value will be dynamically placed when applying the manifest
  spec:
    selector:
      app: {{ .Values.Name }}   # the selector value will be dynamically placed when applying the manifest
  ...
  ```
  
  This becomes very useful when dealing with multiple clusters that share similar configurations (Dev, Prod, Test clusters). 
  Instead of duplicating YAML files for each cluster, Helm enables the creation of parameterized templates.

## Install Helm

```bash
sudo snap install helm --classic
```

## Helm Charts 

Helm uses a packaging format called charts. A chart is a collection of files that describe a related set of Kubernetes resources. 
A single chart might be used to deploy some single application in the cluster.

### Deploy Grafana using Helm

**Remove any existed grafana Deployment, StatefulSet or Service before you start.**

Like DockerHub, there is a open-source community Hub for Charts of famous applications.
It's called [Artifact Hub](https://artifacthub.io/packages/search?kind=0), check it out. 

Let's review and install the [official Helm Chart for Grafana](https://artifacthub.io/packages/helm/grafana/grafana).

To deploy the Grafana Chart, you first have to add the **Repository** in which this Chart exists. 
A Helm Repository is the place where Charts can be collected and shared.

```bash
helm repo add grafana-charts https://grafana.github.io/helm-charts
helm repo update
```

The `grafana-charts` Helm Repository contains many different Charts maintained by the Grafana organization. 
[Among the different Charts](https://artifacthub.io/packages/search?repo=grafana&sort=relevance&page=1) of this repo, there is a Chart used to deploy the Grafana server in Kubernetes. 

Deploy the `grafana` Chart by: 

```bash
helm install grafana grafana-charts/grafana 
```

The command syntax is as follows: `helm install <release-name> <helm-repo-name>/<chart-name>`.

Whenever you install a Chart, a new **Release** is created.   
In the above command, the Grafana server has been released under the name `grafana`, using the `grafana` Chart from the `grafana-rep` repo.

During installation, the Helm client will print useful information about which resources were created, what the state of the Release is, and also whether there are additional configuration steps you can or should take.

### Customize the Grafana release

When installed the Grafana Chart, the server has been release with default configurations that the Chart author decided for you. 

A typical Chart contains hundreds of different configurations, e.g. container's environment variables, custom secrets, etc..

Obviously, you want to customize the Grafana release according to your configurations.
Good Helm Chart should allow you to configure the Release according to your configurations. 

To see what options are configurable on a Chart, go to the [Chart's documentation page](https://artifacthub.io/packages/helm/grafana/grafana), or use the `helm show values grafana-repo/grafana` command. 

Let's override some of the default configurations by specifying them in a YAML file, and then pass that file during the Release upgrade:

```yaml
# k8s/grafana-values.yaml

persistence:
  enabled: true
  size: 2Gi

env:
  GF_DASHBOARDS_VERSIONS_TO_KEEP: 10

```

The above values configure the Grafana server data to be persistent, and define some Grafana related environment variable. 

To apply the new Chart values, `upgrade` the Release: 

```bash
helm upgrade -f grafana-values.yaml grafana grafana-repo/grafana
```

An `upgrade` takes an existing Release and upgrades it according to the information you provide. 
Because Kubernetes Charts can be large and complex, Helm tries to perform the least invasive upgrade. 
It will only update things that have changed since the last release.

If something does not go as planned during a release, it is easy to roll back to a previous release using `helm rollback [RELEASE] [REVISION]`:

```shell
helm rollback grafana 1
```

To uninstall the Chart release:

```shell
helm uninstall grafana
```

## Create your own Helm Chart

In this section we will create a Chart for the `paymentservice` (a component within the [Online Boutique service](https://github.com/GoogleCloudPlatform/microservices-demo)).

Why is it good idea? Imagine the Online Boutique service is a real product at your company. 
The service is probably deployed in at least two different environments: Development and Production. 
Instead of maintaining two different sets of Yaml manifests for with values per environment, we will leverage the created Chart to deploy the application in two instances: first as `paymentservice-dev` for the Development environment, and as `paymentservice-prod` for Production env, each with his own values.

Helm can help you get started quickly by using the `helm create` command:

```bash
helm create paymentservice
```

Now there is a chart in `./paymentservice`. You can edit it and create your own templates.
The directory name is the name of the chart.

Inside of this directory, Helm will expect the following structure:

```text
paymentservice/
  Chart.yaml          # A YAML file containing information about the chart
  values.yaml         # The default configuration values for this chart
  charts/             # A directory containing any charts upon which this chart depends.
  crds/               # Custom Resource Definitions
  templates/          # A directory of templates that, when combined with values,
                      # will generate valid Kubernetes manifest files.
  templates/NOTES.txt # OPTIONAL: A plain text file containing short usage notes
```

For more information about Chart files structure, go to [Helm docs](https://helm.sh/docs/topics/charts/). 

Change the default Chart values in `values.yaml` to match the original `paymentservice` service, as follows:

```yaml
# paymentservice/values.yaml

image:
  repository: gcr.io/google-samples/microservices-demo/paymentservice
  tag: "v0.8.0"

service:
  port: 50051 

resources:
  requests:
    cpu: 50m
    memory: 64Mi
  limits:
    cpu: 200m
    memory: 128Mi
```

As you edit your chart, you can validate that it is well-formed by running `helm lint`.

When it's time to package the chart up for deployment, you can run the `helm package` command:

```bash
helm package paymentservice
```

And that chart can now easily be installed by:

```bash
helm install paymentservice-dev ./paymentservice-0.1.0.tgz
```

# Exercises 

### :pencil2: Redis cluster using Helm

Provision a Redis cluster with 1 master an 2 replicas using [Bitnami Helm Chart](https://artifacthub.io/packages/helm/bitnami/redis) 

Configure the Online Boutique Service to work with your Redis cluster instead of the existed `redis-cart` Deployment.  

Guidelines: 

- Deploy the Helm Chart with it's default values (find the command in the **TL;DR** section in the Chart's docs).
- Take a look on your cluster, find the deployed resources, make sure Redis is up and running by observing the logs. 
- In your local environment, create a values file (e.g. `redis-values.yaml`) with values override according to the requirements. 
- The redis DB is owned by the `cartservice`, find its `Deployment` manifest in `k8s/online-boutique/release-0.8.0.yaml` and change the relevant values to work with your fresh Redis cluster.
- Visit the app (by port forwarding the `frontend` service) and make sure it's work properly. 