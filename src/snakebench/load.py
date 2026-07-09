"""Load and parse parquet telemetry files."""

from pathlib import Path
from typing import Union
import pandas as pd


def load_parquet_files(path: Union[str, Path]) -> pd.DataFrame:
    """
    Load parquet files and concatenate them into a single DataFrame.

    Parameters
    ----------
    path : str or Path
        Path to a directory containing .parquet files or a single .parquet file.

    Returns
    -------
    pd.DataFrame
        Concatenated DataFrame with a 'source_file' column indicating origin.

    Raises
    ------
    ValueError
        If path is a directory with no .parquet files.
    FileNotFoundError
        If path does not exist.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    dfs = []
    failed_files = []

    if path.is_file():
        # Single file case
        if not path.suffix.lower() == ".parquet":
            raise ValueError(f"File is not a parquet file: {path}")
        try:
            df = pd.read_parquet(path)
            df["source_file"] = path.name
            dfs.append(df)
        except Exception as e:
            raise ValueError(f"Failed to read parquet file {path}: {e}")
    else:
        # Directory case
        parquet_files = sorted(path.glob("*.parquet"))

        if not parquet_files:
            raise ValueError(f"No .parquet files found in directory: {path}")

        for file_path in parquet_files:
            try:
                df = pd.read_parquet(file_path)
                df["source_file"] = file_path.name
                dfs.append(df)
            except Exception as e:
                failed_files.append((file_path.name, str(e)))

        if failed_files:
            error_msg = "Failed to read the following parquet files:\n"
            for fname, error in failed_files:
                error_msg += f"  {fname}: {error}\n"
            raise ValueError(error_msg)

    if not dfs:
        raise ValueError(f"No parquet files could be loaded from: {path}")

    result = pd.concat(dfs, ignore_index=True)
    return result
