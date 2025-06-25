# Metrics Generator

## Description:

A basic test app for stresstesting resource limits in OpenShift Container Platform.

It is an instrumented Python-flask application that can be deployed in an openshift-cluster.

## Usage

1. Run the following commands:

  ```
  oc create ns test
  ```

  ```
  oc apply -f .
  ```

2. Once the app is running, generate time series by curl request to the "/generate-high-cardinality" endpoint, as follows

  ```
  curl $(oc -n test get route metrics-generator-route -o jsonpath='{.spec.host}'/generate_high_cardinality_metrics?series_count=10000)
  ```
  
  In which the final number in the endpoint can be adjusted to increase or decrease the number of series generated. i.e. the above command generates 10000 time series.
  
