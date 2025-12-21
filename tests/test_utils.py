"""Tests for devopstoolbox.k8s.utils module."""

from devopstoolbox.k8s.utils import parse_cpu, parse_memory


class TestParseCpu:
    """Tests for parse_cpu function."""

    def test_parse_nanocores(self):
        """Test parsing nanocores to millicores."""
        assert parse_cpu("1000000n") == "1.00m"
        assert parse_cpu("500000n") == "0.50m"
        assert parse_cpu("23434n") == "0.02m"
        assert parse_cpu("25160674n") == "25.16m"

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
