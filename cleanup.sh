helm ls --all --short | xargs -L1 helm uninstall
kubectl delete statefulset mongo
kubectl delete statefulset elasticsearch
kubectl delete cronjobs --all
kubectl delete jobs --all