#!/bin/bash
az ad sp create-for-rbac \
  --name "github-actions-aks-sp" \
  --role Contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP> \
  --sdk-auth
