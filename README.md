# Metrics Generator

## Description:

A basic test app for stresstesting resource limits in OpenShift Container Platform.

It is an instrumented Python-flask application that can be deployed in an openshift-cluster.

## Usage

1. Run the following commands:

  ```
  oc create ns test
  oc project test
  oc apply -f .
  ```

2. Once the app is running, generate time series by curl request to the "/generate-high-cardinality" endpoint, as follows

  ```
  curl $(oc -n test get route metrics-generator-route -o jsonpath='{.spec.host}'/generate_high_cardinality_metrics?series_count=10000)
  ```
  
  In which the final number in the endpoint can be adjusted to increase or decrease the number of series generated. i.e. the above command generates 10000 time series.

3. A HTTP request can be made to the '/health' endpoint with the following curl command:

  ```
  curl $(oc -n test get route metrics-generator-route -o jsonpath='{.spec.host}'/health)
  ```

4. Metrics can be retrieved on the CLI using the following command:

  ```
  curl $(oc -n test get route metrics-generator-route -o jsonpath='{.spec.host}'/metrics)
  ```

4. In the *Observe > Metrics* window of the OCP Administrator console, You may run PromQL Queries to view the resource consumption on various components from the generated metrics

`sum(container_memory_usage_bytes{namespace=~"openshift-user-workload-monitoring"}) by ( namespace)`

`avg_over_time(node_namespace_pod_container:container_memory_working_set_bytes{namespace="openshift-user-workload-monitoring"}[1m])`
