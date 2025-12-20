from kubernetes import client, config, watch
from kubernetes.client import CustomObjectsApi

def get_kube_config():
    try:
        return config.load_kube_config()
    except config.ConfigException:
        return config.load_incluster_config()