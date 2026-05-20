from pathlib import Path
import pandas as pd

from src.region_sorter import RegionSorter


class DataProcessor:

    def load_and_process(self, csv_path: Path) -> pd.DataFrame:
        df = pd.read_csv(csv_path)

        df.columns = df.columns.str.strip().str.lower()

        required = {
            "point_name",
            "latitude",
            "longitude",
            "due_date",
            "arrear_amount",
            "status",
        }

        missing = required - set(df.columns)

        if missing:
            raise ValueError(f"Missing columns: {missing}")

        df["latitude"] = pd.to_numeric(
            df["latitude"],
            errors="coerce",
        )

        df["longitude"] = pd.to_numeric(
            df["longitude"],
            errors="coerce",
        )

        df["arrear_amount"] = pd.to_numeric(
            df["arrear_amount"],
            errors="coerce",
        ).fillna(0)

        df["due_date"] = pd.to_datetime(
            df["due_date"],
            dayfirst=True,
            errors="coerce",
        )

        today = pd.Timestamp.today().normalize()

        df["overdue_days"] = (
            today - df["due_date"]
        ).dt.days

        df["overdue_days"] = df["overdue_days"].fillna(0)

        df["status"] = (
            df["status"]
            .astype(str)
            .str.strip()
            .str.title()
        )

        df = df.dropna(
            subset=[
                "latitude",
                "longitude",
                "due_date",
            ]
        )

        df["timeline_category"] = df["overdue_days"].apply(
            self.get_timeline_category
        )

        df["arrear_category"] = df["arrear_amount"].apply(
            self.get_arrear_category
        )

        sorter = RegionSorter()
        df = sorter.sort_regions(df)

        return df

    def get_timeline_category(self, overdue_days):
        if overdue_days <= 7:
            return "0-7 Days"
        elif overdue_days <= 15:
            return "8-15 Days"
        elif overdue_days <= 30:
            return "16-30 Days"
        return "30+ Days"

    def get_arrear_category(self, amount):
        if amount <= 5000:
            return "0-5K"
        elif amount <= 10000:
            return "5K-10K"
        elif amount <= 25000:
            return "10K-25K"
        return "25K+"

    def apply_filters(
        self,
        df,
        region="All",
        timeline="All",
        arrear="All",
        status="All",
    ):
        filtered = df.copy()

        if region != "All":
            filtered = filtered[
                filtered["region"] == region
            ]

        if timeline != "All":
            filtered = filtered[
                filtered["timeline_category"] == timeline
            ]

        if arrear != "All":
            filtered = filtered[
                filtered["arrear_category"] == arrear
            ]

        if status != "All":
            filtered = filtered[
                filtered["status"] == status
            ]

        return filtered