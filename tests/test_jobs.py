"""Tests for devopstoolbox.k8s.jobs module."""

from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from devopstoolbox.k8s import jobs

runner = CliRunner()


@pytest.fixture(autouse=True)
def mock_kube_config():
    """Mock kubeconfig loading for all tests."""
    with patch("devopstoolbox.k8s.utils.load_kube_config"):
        with patch("devopstoolbox.k8s.jobs.utils.calculate_age", return_value="1h30m"):
            yield


@pytest.fixture
def mock_completed_job():
    """Create a mock completed job object."""
    job = Mock()
    job.metadata.namespace = "default"
    job.metadata.name = "completed-job"
    job.spec.suspend = False
    job.status.start_time = datetime.now(timezone.utc)

    condition = Mock()
    condition.type = "Complete"
    condition.status = "True"
    job.status.conditions = [condition]

    return job


@pytest.fixture
def mock_failed_job():
    """Create a mock failed job object."""
    job = Mock()
    job.metadata.namespace = "default"
    job.metadata.name = "failed-job"
    job.spec.suspend = False
    job.status.start_time = datetime.now(timezone.utc)

    condition = Mock()
    condition.type = "Failed"
    condition.status = "True"
    condition.message = "BackoffLimitExceeded"
    job.status.conditions = [condition]

    return job


@pytest.fixture
def mock_running_job():
    """Create a mock running job object (no conditions yet)."""
    job = Mock()
    job.metadata.namespace = "default"
    job.metadata.name = "running-job"
    job.spec.suspend = False
    job.status.conditions = None
    job.status.start_time = datetime.now(timezone.utc)

    return job


@pytest.fixture
def mock_suspended_job():
    """Create a mock suspended job object."""
    job = Mock()
    job.metadata.namespace = "default"
    job.metadata.name = "suspended-job"
    job.spec.suspend = True
    job.status.conditions = None
    job.status.start_time = datetime.now(timezone.utc)

    return job


class TestJobsListCommand:
    """Tests for jobs list command."""

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_list_jobs_default_namespace(self, mock_api, mock_completed_job):
        """Test listing jobs in default namespace."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_jobs = Mock()
        mock_jobs.items = [mock_completed_job]
        mock_v1.list_namespaced_job.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["list", "-n", "default"])

        assert result.exit_code == 0
        mock_v1.list_namespaced_job.assert_called_once_with(namespace="default", watch=False)

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_list_jobs_specific_namespace_long(self, mock_api, mock_completed_job):
        """Test listing jobs in a specific namespace with long flag."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_jobs = Mock()
        mock_jobs.items = [mock_completed_job]
        mock_v1.list_namespaced_job.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["list", "--namespace", "kube-system"])

        assert result.exit_code == 0
        mock_v1.list_namespaced_job.assert_called_once_with(namespace="kube-system", watch=False)

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_list_jobs_specific_namespace_short(self, mock_api, mock_completed_job):
        """Test listing jobs in a specific namespace with short flag."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_jobs = Mock()
        mock_jobs.items = [mock_completed_job]
        mock_v1.list_namespaced_job.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["list", "-n", "kube-system"])

        assert result.exit_code == 0
        mock_v1.list_namespaced_job.assert_called_once_with(namespace="kube-system", watch=False)

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_list_jobs_all_namespaces_long(self, mock_api, mock_completed_job):
        """Test listing jobs across all namespaces with long flag."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_jobs = Mock()
        mock_jobs.items = [mock_completed_job]
        mock_v1.list_job_for_all_namespaces.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["list", "--all-namespaces"])

        assert result.exit_code == 0
        mock_v1.list_job_for_all_namespaces.assert_called_once_with(watch=False)

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_list_jobs_all_namespaces_short(self, mock_api, mock_completed_job):
        """Test listing jobs across all namespaces with short flag."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_jobs = Mock()
        mock_jobs.items = [mock_completed_job]
        mock_v1.list_job_for_all_namespaces.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["list", "-A"])

        assert result.exit_code == 0
        mock_v1.list_job_for_all_namespaces.assert_called_once_with(watch=False)

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_list_jobs_displays_completed_status(self, mock_api, mock_completed_job):
        """Test that completed jobs show Complete status."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_jobs = Mock()
        mock_jobs.items = [mock_completed_job]
        mock_v1.list_namespaced_job.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["list", "-n", "default"])

        assert result.exit_code == 0
        assert "completed-job" in result.output
        assert "Complete" in result.output

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_list_jobs_displays_failed_status(self, mock_api, mock_failed_job):
        """Test that failed jobs show Failed status."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_jobs = Mock()
        mock_jobs.items = [mock_failed_job]
        mock_v1.list_namespaced_job.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["list", "-n", "default"])

        assert result.exit_code == 0
        assert "failed-job" in result.output
        assert "Failed" in result.output

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_list_jobs_displays_running_status(self, mock_api, mock_running_job):
        """Test that running jobs (no conditions) show Running status."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_jobs = Mock()
        mock_jobs.items = [mock_running_job]
        mock_v1.list_namespaced_job.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["list", "-n", "default"])

        assert result.exit_code == 0
        assert "running-job" in result.output
        assert "Running" in result.output

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_list_jobs_displays_suspended_yes(self, mock_api, mock_suspended_job):
        """Test that suspended jobs show Yes in suspended column."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_jobs = Mock()
        mock_jobs.items = [mock_suspended_job]
        mock_v1.list_namespaced_job.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["list", "-n", "default"])

        assert result.exit_code == 0
        assert "suspended-job" in result.output
        assert "Yes" in result.output

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_list_jobs_displays_suspended_no(self, mock_api, mock_completed_job):
        """Test that non-suspended jobs show No in suspended column."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_jobs = Mock()
        mock_jobs.items = [mock_completed_job]
        mock_v1.list_namespaced_job.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["list", "-n", "default"])

        assert result.exit_code == 0
        assert "No" in result.output

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_list_jobs_handles_no_conditions(self, mock_api):
        """Test handling jobs with no conditions (None)."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        job = Mock()
        job.metadata.namespace = "default"
        job.metadata.name = "pending-job"
        job.spec.suspend = False
        job.status.conditions = None
        job.status.start_time = datetime.now(timezone.utc)

        mock_jobs = Mock()
        mock_jobs.items = [job]
        mock_v1.list_namespaced_job.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["list", "-n", "default"])

        assert result.exit_code == 0
        assert "pending-job" in result.output

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_list_jobs_handles_empty_conditions(self, mock_api):
        """Test handling jobs with empty conditions list."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        job = Mock()
        job.metadata.namespace = "default"
        job.metadata.name = "new-job"
        job.spec.suspend = False
        job.status.conditions = []
        job.status.start_time = datetime.now(timezone.utc)

        mock_jobs = Mock()
        mock_jobs.items = [job]
        mock_v1.list_namespaced_job.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["list", "-n", "default"])

        assert result.exit_code == 0
        assert "new-job" in result.output

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_list_jobs_handles_api_error(self, mock_api):
        """Test handling Kubernetes API errors."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1
        mock_v1.list_namespaced_job.side_effect = Exception("API Error")

        result = runner.invoke(jobs.app, ["list", "-n", "default"])

        assert result.exit_code == 0
        assert "Error" in result.output

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_list_jobs_prioritizes_failed_over_complete(self, mock_api):
        """Test that Failed status takes priority when both conditions exist."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        job = Mock()
        job.metadata.namespace = "default"
        job.metadata.name = "mixed-job"
        job.spec.suspend = False
        job.status.start_time = datetime.now(timezone.utc)

        complete_condition = Mock()
        complete_condition.type = "Complete"
        complete_condition.status = "True"

        failed_condition = Mock()
        failed_condition.type = "Failed"
        failed_condition.status = "True"

        job.status.conditions = [complete_condition, failed_condition]

        mock_jobs = Mock()
        mock_jobs.items = [job]
        mock_v1.list_namespaced_job.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["list", "-n", "default"])

        assert result.exit_code == 0
        assert "Failed" in result.output

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_list_jobs_multiple_jobs(self, mock_api, mock_completed_job, mock_failed_job, mock_running_job):
        """Test listing multiple jobs with different statuses."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_jobs = Mock()
        mock_jobs.items = [mock_completed_job, mock_failed_job, mock_running_job]
        mock_v1.list_namespaced_job.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["list", "-n", "default"])

        assert result.exit_code == 0
        assert "completed-job" in result.output
        assert "failed-job" in result.output
        assert "running-job" in result.output


class TestJobsFailedCommand:
    """Tests for jobs failed command."""

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_failed_jobs_default_namespace(self, mock_api, mock_failed_job):
        """Test listing failed jobs in default namespace."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_jobs = Mock()
        mock_jobs.items = [mock_failed_job]
        mock_v1.list_namespaced_job.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["failed", "-n", "default"])

        assert result.exit_code == 0
        mock_v1.list_namespaced_job.assert_called_once_with(namespace="default", watch=False)

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_failed_jobs_specific_namespace_long(self, mock_api, mock_failed_job):
        """Test listing failed jobs in a specific namespace with long flag."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_jobs = Mock()
        mock_jobs.items = [mock_failed_job]
        mock_v1.list_namespaced_job.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["failed", "--namespace", "kube-system"])

        assert result.exit_code == 0
        mock_v1.list_namespaced_job.assert_called_once_with(namespace="kube-system", watch=False)

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_failed_jobs_specific_namespace_short(self, mock_api, mock_failed_job):
        """Test listing failed jobs in a specific namespace with short flag."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_jobs = Mock()
        mock_jobs.items = [mock_failed_job]
        mock_v1.list_namespaced_job.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["failed", "-n", "kube-system"])

        assert result.exit_code == 0
        mock_v1.list_namespaced_job.assert_called_once_with(namespace="kube-system", watch=False)

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_failed_jobs_all_namespaces_long(self, mock_api, mock_failed_job):
        """Test listing failed jobs across all namespaces with long flag."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_jobs = Mock()
        mock_jobs.items = [mock_failed_job]
        mock_v1.list_job_for_all_namespaces.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["failed", "--all-namespaces"])

        assert result.exit_code == 0
        mock_v1.list_job_for_all_namespaces.assert_called_once_with(watch=False)

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_failed_jobs_all_namespaces_short(self, mock_api, mock_failed_job):
        """Test listing failed jobs across all namespaces with short flag."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_jobs = Mock()
        mock_jobs.items = [mock_failed_job]
        mock_v1.list_job_for_all_namespaces.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["failed", "-A"])

        assert result.exit_code == 0
        mock_v1.list_job_for_all_namespaces.assert_called_once_with(watch=False)

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_failed_jobs_displays_failed_job(self, mock_api, mock_failed_job):
        """Test that failed jobs are displayed."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_jobs = Mock()
        mock_jobs.items = [mock_failed_job]
        mock_v1.list_namespaced_job.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["failed", "-n", "default"])

        assert result.exit_code == 0
        assert "failed-job" in result.output
        assert "Failed" in result.output
        assert "BackoffLimitExceeded" in result.output

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_failed_jobs_filters_completed_jobs(self, mock_api, mock_completed_job, mock_failed_job):
        """Test that completed jobs are filtered out."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_jobs = Mock()
        mock_jobs.items = [mock_completed_job, mock_failed_job]
        mock_v1.list_namespaced_job.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["failed", "-n", "default"])

        assert result.exit_code == 0
        assert "failed-job" in result.output
        assert "completed-job" not in result.output

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_failed_jobs_filters_running_jobs(self, mock_api, mock_running_job, mock_failed_job):
        """Test that running jobs are filtered out."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_jobs = Mock()
        mock_jobs.items = [mock_running_job, mock_failed_job]
        mock_v1.list_namespaced_job.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["failed", "-n", "default"])

        assert result.exit_code == 0
        assert "failed-job" in result.output
        assert "running-job" not in result.output

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_failed_jobs_handles_no_failed_jobs(self, mock_api, mock_completed_job):
        """Test handling when no failed jobs exist."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_jobs = Mock()
        mock_jobs.items = [mock_completed_job]
        mock_v1.list_namespaced_job.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["failed", "-n", "default"])

        assert result.exit_code == 0
        assert "completed-job" not in result.output

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_failed_jobs_handles_api_error(self, mock_api):
        """Test handling Kubernetes API errors."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1
        mock_v1.list_namespaced_job.side_effect = Exception("API Error")

        result = runner.invoke(jobs.app, ["failed", "-n", "default"])

        assert result.exit_code == 0
        assert "Error" in result.output

    @patch("devopstoolbox.k8s.jobs.client.BatchV1Api")
    def test_failed_jobs_multiple_failed(self, mock_api):
        """Test listing multiple failed jobs."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        job1 = Mock()
        job1.metadata.namespace = "default"
        job1.metadata.name = "failed-job-1"
        job1.spec.suspend = False
        job1.status.start_time = datetime.now(timezone.utc)
        condition1 = Mock()
        condition1.type = "Failed"
        condition1.status = "True"
        condition1.message = "Error message 1"
        job1.status.conditions = [condition1]

        job2 = Mock()
        job2.metadata.namespace = "default"
        job2.metadata.name = "failed-job-2"
        job2.spec.suspend = False
        job2.status.start_time = datetime.now(timezone.utc)
        condition2 = Mock()
        condition2.type = "Failed"
        condition2.status = "True"
        condition2.message = "Error message 2"
        job2.status.conditions = [condition2]

        mock_jobs = Mock()
        mock_jobs.items = [job1, job2]
        mock_v1.list_namespaced_job.return_value = mock_jobs

        result = runner.invoke(jobs.app, ["failed", "-n", "default"])

        assert result.exit_code == 0
        assert "failed-job-1" in result.output
        assert "failed-job-2" in result.output
