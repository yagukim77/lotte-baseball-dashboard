import os
import pandas as pd
from pandas.errors import EmptyDataError

def safe_read_csv(path, columns=None):
    try:
        if not os.path.exists(path):
            return pd.DataFrame(columns=columns or [])
        return pd.read_csv(path)
    except EmptyDataError:
        return pd.DataFrame(columns=columns or [])
    except Exception:
        return pd.DataFrame(columns=columns or [])
