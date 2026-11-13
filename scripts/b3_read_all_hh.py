from __future__ import annotations
import zipfile
from pathlib import Path
import pandas as pd

KEEP_COLS = [
    "TIMESTAMP_START", "TIMESTAMP_END", "TA_F", "SW_IN_F", "VPD_F", "P_F",
    "NETRAD", "G_F_MDS", "H_F_MDS", "H_F_MDS_QC", "LE_F_MDS", "LE_F_MDS_QC",
    "NEE_VUT_REF", "NEE_VUT_REF_QC", "GPP_NT_VUT_REF", "RECO_NT_VUT_REF"
]

def read_hh(zip_file: str | Path) -> pd.DataFrame:
    """Read half-hourly FLUXMET data from a FLUXNET zip archive and add a 'site' column."""
    zip_path = Path(zip_file)
    # Filename format: <HUB>_<SITE-ID>_FLUXNET_<YEARS>_... (e.g., AMF_US-SRG_FLUXNET_...)
    site_id = zip_path.name.split("_")[1]

    with zipfile.ZipFile(zip_path) as z:
        hh_name = [n for n in z.namelist() if "FLUXMET_HH" in n][0]
        with z.open(hh_name) as f:
            df = pd.read_csv(
                f,
                na_values=[-9999],
                usecols=lambda c: c in KEEP_COLS,
                dtype={"TIMESTAMP_START": str, "TIMESTAMP_END": str}
            )

    df["time"] = pd.to_datetime(df["TIMESTAMP_START"], format="%Y%m%d%H%M")
    df.insert(0, "site", site_id)
    return df

if __name__ == "__main__":
    zip_files = sorted(Path("data/raw").glob("*.zip"))
    hh_all = pd.concat([read_hh(zf) for zf in zip_files], ignore_index=True)

    print("Combined shape (rows, cols):", hh_all.shape)
    print("\nSummary per site:")
    print(
        hh_all.groupby("site").agg(
            rows=("time", "count"),
            start=("time", "min"),
            end=("time", "max"),
            duplicated_timestamps=("time", lambda s: s.duplicated().sum()),
            ta_min=("TA_F", "min"),
            ta_mean=("TA_F", "mean"),
            ta_max=("TA_F", "max"),
        )
    )
