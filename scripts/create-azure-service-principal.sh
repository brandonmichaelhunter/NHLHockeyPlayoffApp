#!/bin/bash
az ad sp create-for-rbac \
  --name "github-actions-aks-sp" \
  --role Contributor \
  --scopes /subscriptions/852366a7-d993-4535-8128-659688b160da/resourceGroups/<RESOURCE_GROUP> \
  --sdk-auth
