"""Report generation for risk quantification.

Wraps MarkdownExporter for producing human-readable risk reports.
"""

from __future__ import annotations

from .results_aggregator import ResultsAggregator
from .output_formats import MarkdownExporter, JsonExporter


class RiskReportGenerator:
    """Generate risk reports from aggregated results."""

    def __init__(self, title: str = "Collision Risk Quantification Report"):
        self.title = title

    def generate(
        self,
        aggregator: ResultsAggregator,
        output_path: str | None = None,
    ) -> str:
        """Generate markdown report from ResultsAggregator.

        Args:
            aggregator: Aggregated results.
            output_path: Optional file path to write report.

        Returns:
            Markdown report string.
        """
        summary = aggregator.get_summary()
        scenarios_data = {sid: r.to_dict() for sid, r in aggregator.results.items()}

        report = MarkdownExporter.export(
            results=scenarios_data,
            summary=summary,
            output_path=output_path,
        )
        return report

    def generate_json(
        self,
        aggregator: ResultsAggregator,
        output_path: str | Path,
    ) -> Path:
        """Generate JSON report from ResultsAggregator."""
        data = {
            "summary": aggregator.get_summary(),
            "scenarios": {sid: r.to_dict() for sid, r in aggregator.results.items()},
        }
        return JsonExporter.export(data, output_path)

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value
