"""Tests for devopstoolbox.k8s.utils module."""

from unittest.mock import patch

from devopstoolbox.k8s import utils
from devopstoolbox.k8s.utils import calculate_cpu_percentage, calculate_memory_percentage, parse_cpu, parse_memory


class TestParseCpu:
    """Tests for parse_cpu function."""

    def test_parse_nanocores(self):
        """Test parsing nanocores to millicores."""
        assert parse_cpu("1000000n") == "1.00m"
        assert parse_cpu("500000n") == "0.50m"
        assert parse_cpu("23434n") == "0.02m"
        assert parse_cpu("25160674n") == "25.16m"

    def test_parse_microcores(self):
        """Test parsing microcores to millicores."""
        assert parse_cpu("100u") == "0.10m"
        assert parse_cpu("1000u") == "1.00m"
        assert parse_cpu("5000u") == "5.00m"
        assert parse_cpu("500u") == "0.50m"

    def test_parse_millicores(self):
        """Test that millicores are returned as-is."""
        assert parse_cpu("100m") == "100m"
        assert parse_cpu("500m") == "500m"
        assert parse_cpu("1000m") == "1000m"

    def test_parse_whole_cores(self):
        """Test parsing whole cores to millicores."""
        assert parse_cpu("1") == "1000.00m"
        assert parse_cpu("2") == "2000.00m"
        assert parse_cpu("0.5") == "500.00m"

    def test_parse_zero(self):
        """Test parsing zero values."""
        assert parse_cpu("0n") == "0.00m"
        assert parse_cpu("0u") == "0.00m"
        assert parse_cpu("0m") == "0m"
        assert parse_cpu("0") == "0.00m"


class TestParseMemory:
    """Tests for parse_memory function."""

    def test_parse_kibibytes(self):
        """Test parsing Ki to appropriate unit."""
        assert parse_memory("1024Ki") == "1.00 Mi"
        assert parse_memory("512Ki") == "512.00 Ki"
        assert parse_memory("7988Ki") == "7.80 Mi"

    def test_parse_mebibytes(self):
        """Test parsing Mi values."""
        assert parse_memory("1024Mi") == "1.00 Gi"
        assert parse_memory("512Mi") == "512.00 Mi"
        assert parse_memory("100Mi") == "100.00 Mi"

    def test_parse_gibibytes(self):
        """Test parsing Gi values."""
        assert parse_memory("1Gi") == "1.00 Gi"
        assert parse_memory("2Gi") == "2.00 Gi"

    def test_parse_tebibytes(self):
        """Test parsing Ti values."""
        assert parse_memory("1Ti") == "1024.00 Gi"

    def test_parse_bytes(self):
        """Test parsing raw bytes."""
        assert parse_memory("1024") == "1.00 Ki"
        assert parse_memory("512") == "512 B"

    def test_parse_invalid(self):
        """Test that invalid formats are returned as-is."""
        assert parse_memory("invalid") == "invalid"
        assert parse_memory("100MB") == "100MB"

    def test_parse_zero(self):
        """Test parsing zero values."""
        assert parse_memory("0Ki") == "0 B"
        assert parse_memory("0") == "0 B"


class TestCpuPercentage:
    def test_calculate_zero(self):
        assert calculate_cpu_percentage(None, None) == "-"
        assert calculate_cpu_percentage(None, 1000) == "-"
        assert calculate_cpu_percentage(100, None) == "-"

    def test_calculate_invalid(self):
        assert calculate_cpu_percentage("1000", "x") == "-"
        assert calculate_cpu_percentage("x", "1000") == "-"
        assert calculate_cpu_percentage("x", "x") == "-"

    def test_parse_nanocores(self):
        assert calculate_cpu_percentage("10000n", "300000n") == "3.33%"
        assert calculate_cpu_percentage("300000n", "300000n") == "100.00%"

    def test_parse_microcores(self):
        assert calculate_cpu_percentage("100u", "1000u") == "10.00%"
        assert calculate_cpu_percentage("1000u", "1000u") == "100.00%"
        assert calculate_cpu_percentage("500u", "1000u") == "50.00%"

    def test_parse_milicores(self):
        assert calculate_cpu_percentage("10000m", "300000m") == "3.33%"
        assert calculate_cpu_percentage("300000m", "300000m") == "100.00%"

    def test_parse_cores(self):
        assert calculate_cpu_percentage("1", "3") == "33.33%"
        assert calculate_cpu_percentage("3", "3") == "100.00%"

    def test_parse_mix_nanocores_milicores(self):
        assert calculate_cpu_percentage("10000m", "300000000000n") == "3.33%"
        assert calculate_cpu_percentage("300000000000n", "300000m") == "100.00%"


class TestMemoryPercentage:
    def test_calculate_zero(self):
        assert calculate_memory_percentage(None, None) == "-"
        assert calculate_memory_percentage(None, 1000) == "-"
        assert calculate_memory_percentage(100, None) == "-"

    def test_calculate_invalid(self):
        assert calculate_memory_percentage("1000", "x") == "-"
        assert calculate_memory_percentage("x", "1000") == "-"
        assert calculate_memory_percentage("x", "x") == "-"

    def test_alculate_kibibytes(self):
        assert calculate_memory_percentage("1024Ki", "1024Ki") == "100.00%"
        assert calculate_memory_percentage("1024Ki", "512Ki") == "200.00%"
        assert calculate_memory_percentage("512Ki", "1024Ki") == "50.00%"

    def test_calculate_parse_mebibytes(self):
        assert calculate_memory_percentage("1024Mi", "1024Mi") == "100.00%"
        assert calculate_memory_percentage("1024Mi", "512Mi") == "200.00%"
        assert calculate_memory_percentage("512Mi", "1024Mi") == "50.00%"

    def test_calculate_parse_gibibytes(self):
        assert calculate_memory_percentage("1024Gi", "1024Gi") == "100.00%"
        assert calculate_memory_percentage("1024Gi", "512Gi") == "200.00%"
        assert calculate_memory_percentage("512Gi", "1024Gi") == "50.00%"

    def test_calculate_parse_tebibytes(self):
        assert calculate_memory_percentage("1024Ti", "1024Ti") == "100.00%"
        assert calculate_memory_percentage("1024Ti", "512Ti") == "200.00%"
        assert calculate_memory_percentage("512Ti", "1024Ti") == "50.00%"

    def test_calculate_parse_bytes(self):
        assert calculate_memory_percentage("1024", "1024") == "100.00%"
        assert calculate_memory_percentage("1024", "512") == "200.00%"
        assert calculate_memory_percentage("512", "1024") == "50.00%"


class TestLoadKubeConfig:
    """Tests for load_kube_config function."""

    def setup_method(self):
        utils._kube_config_loaded = False

    @patch("devopstoolbox.k8s.utils.config.load_kube_config")
    def test_load_kube_config_success(self, mock_load):
        """Test successful kubeconfig loading."""
        utils.load_kube_config()

        mock_load.assert_called_once()
        assert utils._kube_config_loaded is True

    @patch("devopstoolbox.k8s.utils.config.load_incluster_config")
    @patch("devopstoolbox.k8s.utils.config.load_kube_config")
    def test_load_kube_config_fallback_to_incluster(self, mock_load, mock_incluster):
        """Test fallback to in-cluster config when kubeconfig fails."""
        mock_load.side_effect = utils.config.ConfigException("No kubeconfig")

        utils.load_kube_config()

        mock_load.assert_called_once()
        mock_incluster.assert_called_once()
        assert utils._kube_config_loaded is True

    @patch("devopstoolbox.k8s.utils.config.load_kube_config")
    def test_load_kube_config_only_loads_once(self, mock_load):
        """Test that config is only loaded once."""
        utils.load_kube_config()
        utils.load_kube_config()
        utils.load_kube_config()

        mock_load.assert_called_once()


class TestGetCurrentNamespace:
    """Tests for get_current_namespace function."""

    @patch("devopstoolbox.k8s.utils.config.list_kube_config_contexts")
    def test_get_namespace_from_context(self, mock_contexts):
        """Test getting namespace from active context."""
        mock_contexts.return_value = (
            [],
            {"context": {"namespace": "my-namespace"}},
        )

        result = utils.get_current_namespace()

        assert result == "my-namespace"

    @patch("devopstoolbox.k8s.utils.config.list_kube_config_contexts")
    def test_get_default_when_no_namespace_in_context(self, mock_contexts):
        """Test returning default when no namespace in context."""
        mock_contexts.return_value = (
            [],
            {"context": {}},
        )

        result = utils.get_current_namespace()

        assert result == "default"

    @patch("devopstoolbox.k8s.utils.config.list_kube_config_contexts")
    def test_get_default_on_exception(self, mock_contexts):
        """Test returning default on exception."""
        mock_contexts.side_effect = Exception("No kubeconfig")

        result = utils.get_current_namespace()

        assert result == "default"
