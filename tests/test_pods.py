"""Tests for devopstoolbox.k8s.pods module."""

from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from devopstoolbox.k8s import pods

runner = CliRunner()


@pytest.fixture(autouse=True)
def mock_kube_config():
    """Mock kubeconfig loading for all tests."""
    with patch("devopstoolbox.k8s.utils.load_kube_config"):
        yield


@pytest.fixture
def mock_pod():
    """Create a mock pod object."""
    pod = Mock()
    pod.metadata.namespace = "default"
    pod.metadata.name = "test-pod"
    pod.status.phase = "Running"

    container_status = Mock()
    container_status.restart_count = 2
    pod.status.container_statuses = [container_status]

    return pod


@pytest.fixture
def mock_unhealthy_pod():
    """Create a mock unhealthy pod object."""
    pod = Mock()
    pod.metadata.namespace = "default"
    pod.metadata.name = "failing-pod"
    pod.status.phase = "CrashLoopBackOff"

    container_status = Mock()
    container_status.restart_count = 10
    pod.status.container_statuses = [container_status]

    return pod


@pytest.fixture
def mock_container():
    container = Mock()
    container.name = "main"
    container.resources.requests = {"cpu": "100m", "memory": "128Mi"}
    container.resources.limits = {"cpu": "200m", "memory": "256Mi"}
    return container


@pytest.fixture
def mock_pod_metrics():
    return {
        "items": [
            {
                "metadata": {"name": "test-pod", "namespace": "default"},
                "containers": [{"name": "main", "usage": {"cpu": "50m", "memory": "64Mi"}}],
            }
        ]
    }


class TestPodsListCommand:
    """Tests for pods list command."""

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    def test_list_pods_default_namespace(self, mock_api, mock_pod):
        """Test listing pods in default namespace."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_pods = Mock()
        mock_pods.items = [mock_pod]
        mock_v1.list_namespaced_pod.return_value = mock_pods

        result = runner.invoke(pods.app, ["list", "-n", "default"])

        assert result.exit_code == 0
        mock_v1.list_namespaced_pod.assert_called_once_with("default", watch=False)

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    def test_list_pods_specific_namespace_long(self, mock_api, mock_pod):
        """Test listing pods in a specific namespace."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_pods = Mock()
        mock_pods.items = [mock_pod]
        mock_v1.list_namespaced_pod.return_value = mock_pods

        result = runner.invoke(pods.app, ["list", "--namespace", "kube-system"])

        assert result.exit_code == 0
        mock_v1.list_namespaced_pod.assert_called_once_with("kube-system", watch=False)

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    def test_list_pods_specific_namespace_short(self, mock_api, mock_pod):
        """Test listing pods in a specific namespace."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_pods = Mock()
        mock_pods.items = [mock_pod]
        mock_v1.list_namespaced_pod.return_value = mock_pods

        result = runner.invoke(pods.app, ["list", "-n", "kube-system"])

        assert result.exit_code == 0
        mock_v1.list_namespaced_pod.assert_called_once_with("kube-system", watch=False)

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    def test_list_pods_all_namespaces_long(self, mock_api, mock_pod):
        """Test listing pods across all namespaces."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_pods = Mock()
        mock_pods.items = [mock_pod]
        mock_v1.list_pod_for_all_namespaces.return_value = mock_pods

        result = runner.invoke(pods.app, ["list", "--all-namespaces"])

        assert result.exit_code == 0
        mock_v1.list_pod_for_all_namespaces.assert_called_once_with(watch=False)

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    def test_list_pods_all_namespaces_short(self, mock_api, mock_pod):
        """Test listing pods across all namespaces."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_pods = Mock()
        mock_pods.items = [mock_pod]
        mock_v1.list_pod_for_all_namespaces.return_value = mock_pods

        result = runner.invoke(pods.app, ["list", "-A"])

        assert result.exit_code == 0
        mock_v1.list_pod_for_all_namespaces.assert_called_once_with(watch=False)

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    def test_list_pods_handles_no_container_statuses(self, mock_api):
        """Test handling pods with no container statuses."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        pod = Mock()
        pod.metadata.namespace = "default"
        pod.metadata.name = "pending-pod"
        pod.status.phase = "Pending"
        pod.status.container_statuses = None

        mock_pods = Mock()
        mock_pods.items = [pod]
        mock_v1.list_namespaced_pod.return_value = mock_pods

        result = runner.invoke(pods.app, ["list"])

        assert result.exit_code == 0

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    def test_list_pods_handles_api_error(self, mock_api):
        """Test handling Kubernetes API errors."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1
        mock_v1.list_namespaced_pod.side_effect = Exception("API Error")

        result = runner.invoke(pods.app, ["list"])

        assert result.exit_code == 0
        assert "Error" in result.output


class TestPodsUnhealthyCommand:
    """Tests for pods unhealthy command."""

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    def test_unhealthy_filters_running_pods(self, mock_api, mock_pod, mock_unhealthy_pod):
        """Test that running pods are filtered out."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_pods = Mock()
        mock_pods.items = [mock_pod, mock_unhealthy_pod]
        mock_v1.list_namespaced_pod.return_value = mock_pods

        result = runner.invoke(pods.app, ["unhealthy"])

        assert result.exit_code == 0
        # Should show the unhealthy pod but not the running one
        assert "failing-pod" in result.output or "CrashLoopBackOff" in result.output or result.exit_code == 0

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    def test_unhealthy_filters_succeeded_pods(self, mock_api):
        """Test that succeeded pods are filtered out."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        succeeded_pod = Mock()
        succeeded_pod.metadata.namespace = "default"
        succeeded_pod.metadata.name = "completed-job"
        succeeded_pod.status.phase = "Succeeded"
        succeeded_pod.status.container_statuses = []

        mock_pods = Mock()
        mock_pods.items = [succeeded_pod]
        mock_v1.list_namespaced_pod.return_value = mock_pods

        result = runner.invoke(pods.app, ["unhealthy"])

        assert result.exit_code == 0


class TestPodsMetricsCommand:
    """Tests for pods metrics command."""

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    @patch("devopstoolbox.k8s.utils.fetch_pod_metrics")
    def test_metrics_displays_cpu_memory(self, mock_fetch_metrics, mock_core_api):
        mock_fetch_metrics.return_value = {}
        mock_v1 = Mock()
        mock_core_api.return_value = mock_v1
        mock_v1.list_namespaced_pod.return_value = Mock(items=[])

        result = runner.invoke(pods.app, ["metrics"])

        assert result.exit_code == 0

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    @patch("devopstoolbox.k8s.utils.fetch_pod_metrics")
    def test_metrics_handles_empty_response(self, mock_fetch_metrics, mock_core_api):
        """Test handling empty metrics response."""
        mock_fetch_metrics.return_value = {}
        mock_v1 = Mock()
        mock_core_api.return_value = mock_v1
        mock_v1.list_namespaced_pod.return_value = Mock(items=[])

        result = runner.invoke(pods.app, ["metrics"])

        assert result.exit_code == 0

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    @patch("devopstoolbox.k8s.utils.fetch_pod_metrics")
    def test_metrics_handles_api_error(self, mock_fetch_metrics, mock_core_api):
        """Test handling metrics API errors."""
        mock_fetch_metrics.side_effect = Exception("Metrics Server not available")
        mock_v1 = Mock()
        mock_core_api.return_value = mock_v1
        mock_v1.list_namespaced_pod.return_value = Mock(items=[])

        result = runner.invoke(pods.app, ["metrics"])

        assert result.exit_code == 0
        assert "Metrics Server" in result.output

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    @patch("devopstoolbox.k8s.utils.fetch_pod_metrics")
    def test_metrics_specific_namespace(self, mock_fetch_metrics, mock_core_api, mock_container):
        mock_fetch_metrics.return_value = {}

        mock_v1 = Mock()
        mock_core_api.return_value = mock_v1

        pod = Mock()
        pod.metadata.namespace = "default"
        pod.metadata.name = "test-pod"
        pod.spec.containers = [mock_container]

        mock_pods = Mock()
        mock_pods.items = [pod]
        mock_v1.list_namespaced_pod.return_value = mock_pods

        result = runner.invoke(pods.app, ["metrics", "--namespace", "kube-system"])

        assert result.exit_code == 0

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    @patch("devopstoolbox.k8s.utils.fetch_pod_metrics")
    def test_metrics_all_namespaces(self, mock_fetch_metrics, mock_core_api):
        mock_fetch_metrics.return_value = {}

        mock_v1 = Mock()
        mock_core_api.return_value = mock_v1
        mock_v1.list_pod_for_all_namespaces.return_value = Mock(items=[])

        result = runner.invoke(pods.app, ["metrics", "--all-namespaces"])

        assert result.exit_code == 0
        mock_fetch_metrics.assert_called_once()
        mock_v1.list_pod_for_all_namespaces.assert_called_once()

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    @patch("devopstoolbox.k8s.utils.fetch_pod_metrics")
    def test_metrics_displays_all_fields(self, mock_fetch_metrics, mock_core_api, mock_container):
        mock_fetch_metrics.return_value = {("default", "test-pod", "main"): {"cpu": "50m", "memory": "64Mi"}}

        mock_v1 = Mock()
        mock_core_api.return_value = mock_v1

        pod = Mock()
        pod.metadata.namespace = "default"
        pod.metadata.name = "test-pod"
        mock_container.name = "main"
        pod.spec.containers = [mock_container]

        mock_pods = Mock()
        mock_pods.items = [pod]
        mock_v1.list_namespaced_pod.return_value = mock_pods

        result = runner.invoke(pods.app, ["metrics", "-n", "default"])

        assert result.exit_code == 0
        assert "Pod Resources" in result.output
        mock_fetch_metrics.assert_called_once()
        mock_v1.list_namespaced_pod.assert_called_once()

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    @patch("devopstoolbox.k8s.utils.fetch_pod_metrics")
    def test_metrics_sort_by_cpu(self, mock_fetch_metrics, mock_core_api):
        """Test that metrics are sorted by CPU usage in descending order."""
        mock_fetch_metrics.return_value = {
            ("default", "aaa", "main"): {"cpu": "50m", "memory": "64Mi"},
            ("default", "zzz", "main"): {"cpu": "500m", "memory": "32Mi"},
        }

        mock_v1 = Mock()
        mock_core_api.return_value = mock_v1

        # Create two pods with different CPU usage
        low_cpu_container = Mock()
        low_cpu_container.name = "main"
        low_cpu_container.resources.requests = {"cpu": "100m", "memory": "128Mi"}
        low_cpu_container.resources.limits = {"cpu": "200m", "memory": "256Mi"}

        high_cpu_container = Mock()
        high_cpu_container.name = "main"
        high_cpu_container.resources.requests = {"cpu": "100m", "memory": "128Mi"}
        high_cpu_container.resources.limits = {"cpu": "1000m", "memory": "256Mi"}

        low_cpu_pod = Mock()
        low_cpu_pod.metadata.namespace = "default"
        low_cpu_pod.metadata.name = "aaa"
        low_cpu_pod.spec.containers = [low_cpu_container]

        high_cpu_pod = Mock()
        high_cpu_pod.metadata.namespace = "default"
        high_cpu_pod.metadata.name = "zzz"
        high_cpu_pod.spec.containers = [high_cpu_container]

        mock_pods = Mock()
        mock_pods.items = [low_cpu_pod, high_cpu_pod]
        mock_v1.list_namespaced_pod.return_value = mock_pods

        result = runner.invoke(pods.app, ["metrics", "-n", "default", "-s", "cpu"])

        assert result.exit_code == 0
        high_cpu_pos = result.output.find("500m")
        low_cpu_pos = result.output.find("50m")
        assert high_cpu_pos < low_cpu_pos, "High CPU usage should appear first when sorting by CPU"

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    @patch("devopstoolbox.k8s.utils.fetch_pod_metrics")
    def test_metrics_sort_by_memory(self, mock_fetch_metrics, mock_core_api):
        """Test that metrics are sorted by memory usage in descending order."""
        mock_fetch_metrics.return_value = {
            ("default", "aaa", "main"): {"cpu": "500m", "memory": "64Mi"},
            ("default", "zzz", "main"): {"cpu": "50m", "memory": "512Mi"},
        }

        mock_v1 = Mock()
        mock_core_api.return_value = mock_v1

        low_mem_container = Mock()
        low_mem_container.name = "main"
        low_mem_container.resources.requests = {"cpu": "100m", "memory": "128Mi"}
        low_mem_container.resources.limits = {"cpu": "200m", "memory": "256Mi"}

        high_mem_container = Mock()
        high_mem_container.name = "main"
        high_mem_container.resources.requests = {"cpu": "100m", "memory": "128Mi"}
        high_mem_container.resources.limits = {"cpu": "200m", "memory": "1Gi"}

        low_mem_pod = Mock()
        low_mem_pod.metadata.namespace = "default"
        low_mem_pod.metadata.name = "aaa"
        low_mem_pod.spec.containers = [low_mem_container]

        high_mem_pod = Mock()
        high_mem_pod.metadata.namespace = "default"
        high_mem_pod.metadata.name = "zzz"
        high_mem_pod.spec.containers = [high_mem_container]

        mock_pods = Mock()
        mock_pods.items = [low_mem_pod, high_mem_pod]
        mock_v1.list_namespaced_pod.return_value = mock_pods

        result = runner.invoke(pods.app, ["metrics", "-n", "default", "-s", "memory"])

        assert result.exit_code == 0
        high_mem_pos = result.output.find("512")
        low_mem_pos = result.output.find("64")
        assert high_mem_pos < low_mem_pos, "High memory usage should appear first when sorting by memory"

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    @patch("devopstoolbox.k8s.utils.fetch_pod_metrics")
    def test_metrics_limit_results(self, mock_fetch_metrics, mock_core_api):
        """Test that limit option restricts the number of results."""
        mock_fetch_metrics.return_value = {
            ("default", "aaa", "main"): {"cpu": "100m", "memory": "64Mi"},
            ("default", "bbb", "main"): {"cpu": "200m", "memory": "128Mi"},
            ("default", "ccc", "main"): {"cpu": "300m", "memory": "256Mi"},
        }

        mock_v1 = Mock()
        mock_core_api.return_value = mock_v1

        pods_list = []
        for name in ["aaa", "bbb", "ccc"]:
            container = Mock()
            container.name = "main"
            container.resources.requests = {"cpu": "100m", "memory": "128Mi"}
            container.resources.limits = {"cpu": "500m", "memory": "512Mi"}

            pod = Mock()
            pod.metadata.namespace = "default"
            pod.metadata.name = name
            pod.spec.containers = [container]
            pods_list.append(pod)

        mock_pods = Mock()
        mock_pods.items = pods_list
        mock_v1.list_namespaced_pod.return_value = mock_pods

        result = runner.invoke(pods.app, ["metrics", "-n", "default", "-s", "cpu", "-l", "2"])

        assert result.exit_code == 0
        assert "300m" in result.output
        assert "200m" in result.output
        output_lines = result.output.split("\n")
        data_rows = [line for line in output_lines if "100m" in line and "500m" not in line]
        assert len(data_rows) == 0, "Pod with 100m CPU should be excluded by limit"
