import zipfile
from pathlib import Path
import pandas as pd

keep = ["TIMESTAMP_START", "TIMESTAMP_END", "TA_F", "SW_IN_F", "VPD_F", "P_F",
        "NETRAD", "G_F_MDS", "H_F_MDS", "H_F_MDS_QC", "LE_F_MDS", "LE_F_MDS_QC",
        "NEE_VUT_REF", "NEE_VUT_REF_QC", "GPP_NT_VUT_REF", "RECO_NT_VUT_REF"]

zip_file = sorted(Path("data/raw").glob("*.zip"))[0]
with zipfile.ZipFile(zip_file) as z:
    hh_name = [n for n in z.namelist() if "FLUXMET_HH" in n][0]
    with z.open(hh_name) as f:
        hh = pd.read_csv(f, na_values=[-9999],
                         usecols=lambda c: c in keep,
                         dtype={"TIMESTAMP_START": str, "TIMESTAMP_END": str})

hh["time"] = pd.to_datetime(hh["TIMESTAMP_START"], format="%Y%m%d%H%M")
print("Rows & range:", len(hh), hh["time"].min(), hh["time"].max())
print("Measured NEE share:", (hh["NEE_VUT_REF_QC"] == 0).mean())
print("\nRows per year:\n", hh["time"].dt.year.value_counts().sort_index())
print("\nDuplicated timestamps:", hh["time"].duplicated().sum())
print("\nTA_F summary:\n", hh["TA_F"].describe())
