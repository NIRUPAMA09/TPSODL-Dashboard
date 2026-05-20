import pandas as pd


class RegionSorter:

    def sort_regions(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        north_cutoff = df["latitude"].quantile(0.67)
        south_cutoff = df["latitude"].quantile(0.33)

        def classify(lat):
            if lat >= north_cutoff:
                return "North"
            elif lat <= south_cutoff:
                return "South"
            return "Central"

        df["region"] = df["latitude"].apply(classify)

        return df