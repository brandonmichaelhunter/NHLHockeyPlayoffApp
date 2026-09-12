param managedClusters_nhlplayoffapp_cluster_name string = 'nhlplayoffapp_cluster'
param userAssignedIdentities_nhlplayoffapp_cluster_agentpool_externalid string = '/subscriptions/852366a7-d993-4535-8128-659688b160da/resourceGroups/MC_nhlplayoffapp_rg_nhlplayoffapp_cluster_eastus/providers/Microsoft.ManagedIdentity/userAssignedIdentities/nhlplayoffapp_cluster-agentpool'

resource managedClusters_nhlplayoffapp_cluster_name_resource 'Microsoft.ContainerService/managedClusters@2026-04-02-preview' = {
  name: managedClusters_nhlplayoffapp_cluster_name
  location: 'eastus'
  sku: {
    name: 'Base'
    tier: 'Free'
  }
  kind: 'Base'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    kubernetesVersion: '1.35.6'
    dnsPrefix: 'nhlplayoffapp'
    agentPoolProfiles: [
      {
        name: 'agentpool'
        count: 1
        vmSize: 'Standard_D2ps_v6'
        osDiskSizeGB: 128
        osDiskType: 'Managed'
        kubeletDiskType: 'OS'
        maxPods: 110
        type: 'VirtualMachineScaleSets'
        availabilityZones: [
          '1'
          '2'
          '3'
        ]
        enableAutoScaling: false
        scaleDownMode: 'Delete'
        powerState: {
          code: 'Stopped'
        }
        orchestratorVersion: '1.35.6'
        enableNodePublicIP: false
        mode: 'System'
        osType: 'Linux'
        osSKU: 'Ubuntu'
        nodeImageVersion: 'AKSUbuntu-2404gen2arm64containerd-202607.02.0'
        upgradeStrategy: 'Rolling'
        upgradeSettings: {
          maxSurge: '10%'
          maxUnavailable: '0'
        }
        enableFIPS: false
        securityProfile: {
          sshAccess: 'LocalUser'
          enableVTPM: false
          enableSecureBoot: false
        }
      }
    ]
    windowsProfile: {
      adminUsername: 'azureuser'
      enableCSIProxy: true
    }
    servicePrincipalProfile: {
      clientId: 'msi'
    }
    addonProfiles: {
      azureKeyvaultSecretsProvider: {
        enabled: false
      }
      azurepolicy: {
        enabled: false
      }
      extensionManager: {
        enabled: true
      }
    }
    nodeResourceGroup: 'MC_nhlplayoffapp_rg_${managedClusters_nhlplayoffapp_cluster_name}_eastus'
    enableRBAC: true
    supportPlan: 'KubernetesOfficial'
    networkProfile: {
      networkPlugin: 'azure'
      networkPluginMode: 'overlay'
      networkPolicy: 'none'
      networkDataplane: 'azure'
      loadBalancerSku: 'Standard'
      loadBalancerProfile: {
        managedOutboundIPs: {
          count: 1
        }
        backendPoolType: 'nodeIPConfiguration'
      }
      podCidr: '10.244.0.0/16'
      serviceCidr: '10.0.0.0/16'
      dnsServiceIP: '10.0.0.10'
      outboundType: 'loadBalancer'
      podCidrs: [
        '10.244.0.0/16'
      ]
      serviceCidrs: [
        '10.0.0.0/16'
      ]
      ipFamilies: [
        'IPv4'
      ]
      advancedNetworking: {
        enabled: false
        observability: {
          enabled: false
        }
        security: {
          enabled: false
          advancedNetworkPolicies: 'None'
        }
        performance: {
          accelerationMode: 'None'
        }
      }
      podLinkLocalAccess: 'IMDS'
    }
    apiServerAccessProfile: {
      enablePrivateCluster: false
    }
    identityProfile: {
      kubeletidentity: {
        resourceId: userAssignedIdentities_nhlplayoffapp_cluster_agentpool_externalid
        clientId: 'ad8adc27-707b-4ac3-ab49-3227d18e5839'
        objectId: '8407796c-6749-48de-ba09-8080651c15b8'
      }
    }
    autoUpgradeProfile: {
      upgradeChannel: 'none'
      nodeOSUpgradeChannel: 'NodeImage'
    }
    disableLocalAccounts: false
    securityProfile: {
      imageCleaner: {
        enabled: true
        intervalHours: 168
      }
      workloadIdentity: {
        enabled: true
      }
    }
    storageProfile: {
      diskCSIDriver: {
        enabled: true
      }
      fileCSIDriver: {
        enabled: true
      }
      snapshotController: {
        enabled: true
      }
    }
    oidcIssuerProfile: {
      enabled: true
    }
    nodeDisruptionProfile: {
      nodeDisruptionPolicy: 'Allow'
    }
    workloadAutoScalerProfile: {}
    azureMonitorProfile: {
      metrics: {
        enabled: true
        kubeStateMetrics: {}
      }
    }
    metricsProfile: {
      costAnalysis: {
        enabled: false
      }
    }
    nodeProvisioningProfile: {
      mode: 'Manual'
    }
    bootstrapProfile: {
      artifactSource: 'Direct'
    }
    hostedSystemProfile: {
      enabled: false
    }
    enableFIPS: false
    healthMonitorProfile: {
      enableContinuousControlPlaneAndAddonMonitor: false
      enableOnDemandMonitor: false
    }
  }
}

resource managedClusters_nhlplayoffapp_cluster_name_agentpool 'Microsoft.ContainerService/managedClusters/agentPools@2026-04-02-preview' = {
  parent: managedClusters_nhlplayoffapp_cluster_name_resource
  name: 'agentpool'
  properties: {
    count: 1
    vmSize: 'Standard_D2ps_v6'
    osDiskSizeGB: 128
    osDiskType: 'Managed'
    kubeletDiskType: 'OS'
    maxPods: 110
    type: 'VirtualMachineScaleSets'
    availabilityZones: [
      '1'
      '2'
      '3'
    ]
    enableAutoScaling: false
    scaleDownMode: 'Delete'
    powerState: {
      code: 'Stopped'
    }
    orchestratorVersion: '1.35.6'
    enableNodePublicIP: false
    mode: 'System'
    osType: 'Linux'
    osSKU: 'Ubuntu'
    nodeImageVersion: 'AKSUbuntu-2404gen2arm64containerd-202607.02.0'
    upgradeStrategy: 'Rolling'
    upgradeSettings: {
      maxSurge: '10%'
      maxUnavailable: '0'
    }
    enableFIPS: false
    securityProfile: {
      sshAccess: 'LocalUser'
      enableVTPM: false
      enableSecureBoot: false
    }
  }
}

resource managedClusters_nhlplayoffapp_cluster_name_aksManagedNodeOSUpgradeSchedule 'Microsoft.ContainerService/managedClusters/maintenanceConfigurations@2026-04-02-preview' = {
  parent: managedClusters_nhlplayoffapp_cluster_name_resource
  name: 'aksManagedNodeOSUpgradeSchedule'
  properties: {
    maintenanceWindow: {
      schedule: {
        weekly: {
          intervalWeeks: 1
          dayOfWeek: 'Sunday'
        }
      }
      durationHours: 8
      utcOffset: '+00:00'
      startDate: '2026-07-17'
      startTime: '00:00'
    }
  }
}
