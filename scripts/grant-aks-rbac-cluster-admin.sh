az role assignment create \
  --assignee "<app-id>" \
  --role "Azure Kubernetes Service RBAC Cluster Admin" \
  --scope "/subscriptions/<subscription-id>/resourceGroups/<resource-group-name>/providers/Microsoft.ContainerService/managedClusters/<cluster-name>" \