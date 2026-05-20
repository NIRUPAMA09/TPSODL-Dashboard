from pathlib import Path
import pandas as pd


class ReportGenerator:

    def generate_summary(
        self,
        df: pd.DataFrame,
        output_file: Path,
    ):
        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if df.empty:
            summary = pd.DataFrame(
                columns=[
                    "region",
                    "customer_count",
                    "total_arrear_amount",
                    "average_arrear_amount",
                    "max_overdue_days",
                ]
            )

        else:
            summary = (
                df.groupby("region")
                .agg(
                    customer_count=("point_name", "count"),
                    total_arrear_amount=("arrear_amount", "sum"),
                    average_arrear_amount=("arrear_amount", "mean"),
                    max_overdue_days=("overdue_days", "max"),
                )
                .reset_index()
            )

        summary.to_csv(output_file, index=False)

        return summary