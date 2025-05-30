# Idle Shutdown Container

Shutdown Node/Cluster when idle. I use this container on my single node ai cluster to shutdown when all jobs are done.

## Usage

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: ${APP_NAME}
  namespace: ${APP_NAMESPACE}
spec:
  interval: 10m
  chart:
    spec:
      chart: app-template
      version: 3.7.1
      sourceRef:
        kind: HelmRepository
        name: bjw-s-charts
        namespace: flux-system

  values:
    defaultPodOptions:
      runtimeClassName: "nvidia"
    controllers:
      ${APP_NAME}:
        containers:
          app:
            securityContext:
              privileged: true
            image:
              repository: git.gpu.lan/r/idle-shutdown-docker
              tag: "latest"
              pullPolicy: Always
            env:
              NVIDIA_VISIBLE_DEVICES: all
              NVIDIA_DRIVER_CAPABILITIES: all

    persistence:
      data:
        type: hostPath
        hostPath: /
        globalMounts:
          - path: /host
```
