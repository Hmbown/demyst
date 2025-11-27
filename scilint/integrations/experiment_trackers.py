"""
Experiment Tracker Integrations: WandB and MLflow

Provides integration with popular experiment tracking platforms to:
    1. Automatically track number of experiments
    2. Apply Bonferroni correction to reported results
    3. Detect cherry-picking
    4. Generate reproducibility reports
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from datetime import datetime
import json
import warnings


@dataclass
class ExperimentMetadata:
    """Metadata about an experiment run."""
    run_id: str
    timestamp: str
    seed: int
    config: Dict[str, Any]
    metrics: Dict[str, float]
    tags: List[str]


class WandBIntegration:
    """
    Integration with Weights & Biases for experiment tracking with
    scientific integrity enforcement.

    Usage:
        from scilint.integrations.experiment_trackers import WandBIntegration

        tracker = WandBIntegration(project="my-project")
        tracker.init(config={"lr": 0.001, "seed": 42})

        # Log metrics as usual
        tracker.log({"loss": 0.5, "accuracy": 0.9})

        # Get integrity report
        report = tracker.get_integrity_report()
    """

    def __init__(self, project: str, entity: Optional[str] = None):
        """
        Initialize WandB integration.

        Args:
            project: WandB project name
            entity: WandB entity (team/user)
        """
        self.project = project
        self.entity = entity
        self._run = None
        self._experiments: List[ExperimentMetadata] = []
        self._current_seed: Optional[int] = None
        self._current_config: Dict[str, Any] = {}
        self._local_metrics: Dict[str, List[float]] = {}

    def init(self, config: Optional[Dict[str, Any]] = None,
            seed: Optional[int] = None, **kwargs):
        """
        Initialize a new run with integrity tracking.

        Args:
            config: Run configuration
            seed: Random seed for reproducibility
            **kwargs: Additional wandb.init arguments
        """
        self._current_config = config or {}
        self._current_seed = seed or self._current_config.get('seed', 0)
        self._local_metrics = {}

        try:
            import wandb

            # Add scilint metadata to config
            full_config = {
                **self._current_config,
                'scilint_tracked': True,
                'scilint_seed': self._current_seed,
                'scilint_timestamp': datetime.now().isoformat(),
            }

            self._run = wandb.init(
                project=self.project,
                entity=self.entity,
                config=full_config,
                **kwargs
            )

        except ImportError:
            warnings.warn("wandb not installed. Running in local-only mode.")
            self._run = None

    def log(self, metrics: Dict[str, float], step: Optional[int] = None):
        """
        Log metrics with integrity tracking.

        Args:
            metrics: Dictionary of metrics to log
            step: Optional step number
        """
        # Track locally for analysis
        for key, value in metrics.items():
            if key not in self._local_metrics:
                self._local_metrics[key] = []
            self._local_metrics[key].append(value)

        # Log to wandb if available
        if self._run is not None:
            try:
                import wandb
                wandb.log(metrics, step=step)
            except Exception as e:
                warnings.warn(f"Failed to log to wandb: {e}")

    def finish(self):
        """
        Finish the current run and record experiment metadata.
        """
        # Record experiment
        final_metrics = {
            k: v[-1] if v else None
            for k, v in self._local_metrics.items()
        }

        run_id = self._run.id if self._run else f"local_{datetime.now().timestamp()}"

        experiment = ExperimentMetadata(
            run_id=run_id,
            timestamp=datetime.now().isoformat(),
            seed=self._current_seed or 0,
            config=self._current_config,
            metrics=final_metrics,
            tags=['scilint_tracked']
        )
        self._experiments.append(experiment)

        # Finish wandb run
        if self._run is not None:
            try:
                import wandb
                wandb.finish()
            except Exception:
                pass

        self._run = None

    def get_all_experiments(self) -> List[ExperimentMetadata]:
        """Get all tracked experiments."""
        return self._experiments

    def get_integrity_report(self, metric_name: str = 'accuracy',
                            reported_value: Optional[float] = None) -> Dict[str, Any]:
        """
        Generate a scientific integrity report.

        Args:
            metric_name: Name of the primary metric
            reported_value: Value being reported (for cherry-picking analysis)

        Returns:
            Integrity report with statistical corrections
        """
        if not self._experiments:
            return {'error': 'No experiments tracked'}

        # Collect metric values
        values = []
        for exp in self._experiments:
            if metric_name in exp.metrics and exp.metrics[metric_name] is not None:
                values.append(exp.metrics[metric_name])

        if not values:
            return {'error': f'No values found for metric {metric_name}'}

        n_experiments = len(values)
        mean_val = sum(values) / n_experiments
        variance = sum((v - mean_val) ** 2 for v in values) / n_experiments
        std_val = variance ** 0.5

        # Seeds used
        seeds = [exp.seed for exp in self._experiments]

        report = {
            'metric': metric_name,
            'num_experiments': n_experiments,
            'seeds_used': seeds,
            'mean': mean_val,
            'std': std_val,
            'min': min(values),
            'max': max(values),
            'all_values': values,
        }

        # Bonferroni correction
        report['bonferroni_factor'] = n_experiments
        report['corrected_alpha'] = 0.05 / n_experiments

        # Cherry-picking analysis
        if reported_value is not None:
            sorted_vals = sorted(values, reverse=True)
            try:
                rank = sorted_vals.index(reported_value) + 1
            except ValueError:
                rank = None

            report['reported_value'] = reported_value
            report['rank'] = rank
            report['is_best'] = rank == 1 if rank else False

            if rank == 1:
                report['cherry_picking_warning'] = (
                    f"WARNING: Reported value is the best out of {n_experiments} runs. "
                    f"This has a {100/n_experiments:.1f}% probability by chance alone."
                )

        # Verdict
        if n_experiments > 10 and report.get('is_best', False):
            report['verdict'] = (
                f"INVALID: Reporting best of {n_experiments} is cherry-picking. "
                f"Report mean ({mean_val:.4f}) and std ({std_val:.4f}) instead."
            )
        elif n_experiments > 1:
            report['verdict'] = (
                f"Valid with {n_experiments} experiments. Report: "
                f"{mean_val:.4f} +/- {std_val:.4f}"
            )
        else:
            report['verdict'] = (
                "WARNING: Only 1 experiment. Run multiple seeds for statistical validity."
            )

        return report


class MLflowIntegration:
    """
    Integration with MLflow for experiment tracking with
    scientific integrity enforcement.

    Usage:
        from scilint.integrations.experiment_trackers import MLflowIntegration

        tracker = MLflowIntegration(experiment_name="my-experiment")
        tracker.start_run(seed=42)

        # Log metrics
        tracker.log_metric("accuracy", 0.9)

        # Get integrity report
        report = tracker.get_integrity_report()
    """

    def __init__(self, experiment_name: str,
                tracking_uri: Optional[str] = None):
        """
        Initialize MLflow integration.

        Args:
            experiment_name: MLflow experiment name
            tracking_uri: MLflow tracking server URI
        """
        self.experiment_name = experiment_name
        self.tracking_uri = tracking_uri
        self._experiments: List[ExperimentMetadata] = []
        self._current_run_id: Optional[str] = None
        self._current_seed: int = 0
        self._current_params: Dict[str, Any] = {}
        self._local_metrics: Dict[str, List[float]] = {}

    def start_run(self, seed: int = 0, params: Optional[Dict[str, Any]] = None,
                 run_name: Optional[str] = None):
        """
        Start a new MLflow run.

        Args:
            seed: Random seed
            params: Run parameters
            run_name: Optional run name
        """
        self._current_seed = seed
        self._current_params = params or {}
        self._local_metrics = {}

        try:
            import mlflow

            if self.tracking_uri:
                mlflow.set_tracking_uri(self.tracking_uri)

            mlflow.set_experiment(self.experiment_name)
            run = mlflow.start_run(run_name=run_name)
            self._current_run_id = run.info.run_id

            # Log scilint metadata
            mlflow.log_params({
                **self._current_params,
                'scilint_seed': seed,
                'scilint_tracked': True,
            })

        except ImportError:
            warnings.warn("mlflow not installed. Running in local-only mode.")
            self._current_run_id = f"local_{datetime.now().timestamp()}"

    def log_metric(self, key: str, value: float, step: Optional[int] = None):
        """
        Log a metric value.

        Args:
            key: Metric name
            value: Metric value
            step: Optional step number
        """
        if key not in self._local_metrics:
            self._local_metrics[key] = []
        self._local_metrics[key].append(value)

        try:
            import mlflow
            mlflow.log_metric(key, value, step=step)
        except ImportError:
            pass
        except Exception as e:
            warnings.warn(f"Failed to log to mlflow: {e}")

    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """Log multiple metrics."""
        for key, value in metrics.items():
            self.log_metric(key, value, step)

    def end_run(self):
        """End the current run."""
        final_metrics = {
            k: v[-1] if v else None
            for k, v in self._local_metrics.items()
        }

        experiment = ExperimentMetadata(
            run_id=self._current_run_id or 'unknown',
            timestamp=datetime.now().isoformat(),
            seed=self._current_seed,
            config=self._current_params,
            metrics=final_metrics,
            tags=['scilint_tracked']
        )
        self._experiments.append(experiment)

        try:
            import mlflow
            mlflow.end_run()
        except ImportError:
            pass

        self._current_run_id = None

    def get_all_experiments(self) -> List[ExperimentMetadata]:
        """Get all tracked experiments."""
        return self._experiments

    def get_integrity_report(self, metric_name: str = 'accuracy',
                            reported_value: Optional[float] = None) -> Dict[str, Any]:
        """
        Generate a scientific integrity report.

        Identical interface to WandBIntegration for interoperability.
        """
        if not self._experiments:
            return {'error': 'No experiments tracked'}

        values = []
        for exp in self._experiments:
            if metric_name in exp.metrics and exp.metrics[metric_name] is not None:
                values.append(exp.metrics[metric_name])

        if not values:
            return {'error': f'No values found for metric {metric_name}'}

        n = len(values)
        mean_val = sum(values) / n
        variance = sum((v - mean_val) ** 2 for v in values) / n
        std_val = variance ** 0.5

        seeds = [exp.seed for exp in self._experiments]

        report = {
            'metric': metric_name,
            'num_experiments': n,
            'seeds_used': seeds,
            'mean': mean_val,
            'std': std_val,
            'min': min(values),
            'max': max(values),
            'bonferroni_factor': n,
            'corrected_alpha': 0.05 / n,
        }

        if reported_value is not None:
            sorted_vals = sorted(values, reverse=True)
            try:
                rank = sorted_vals.index(reported_value) + 1
                report['rank'] = rank
                report['is_best'] = rank == 1
                if rank == 1:
                    report['cherry_picking_warning'] = (
                        f"Reported best of {n} runs"
                    )
            except ValueError:
                report['rank'] = None

        if n > 10 and report.get('is_best', False):
            report['verdict'] = f"Cherry-picking detected. Report mean instead."
        elif n > 1:
            report['verdict'] = f"Valid: {mean_val:.4f} +/- {std_val:.4f} ({n} runs)"
        else:
            report['verdict'] = "Run multiple seeds for validity."

        return report
