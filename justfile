repo:
  werf helm repo add bitnami https://charts.bitnami.com/bitnami
  
deps:
  werf helm dependency update .helm

secrets:
  gh secret set KUBE_CONFIG_BASE64_DATA --repos=\"$(git remote get-url origin)\" -b$(doctl kubernetes cluster kubeconfig show ekp | base64)
