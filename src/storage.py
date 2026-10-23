import logging

logger = logging.getLogger(__name__)


class DatasetStorage:
    def __init__(self):
        self._store = {}
        self._counter = 0

    def save(self, df, filename):
        """Store a copy of the data and return a new integer ID."""
        self._counter += 1
        self._store[self._counter] = [df.copy(), filename]
        logger.debug(f"Saved a dataframe with integer ID {self._counter} from path {filename}")
        return self._counter
        
    def get(self, dataset_id):
        """Return a copy of the stored DataFrame, or None."""
        if dataset_id in self._store:
            logger.debug(f"Got a copy of DataFrame with ID {dataset_id}")
            return self._store[dataset_id].copy()
        else:
            logger.debug(f"Failed to find a DataFrame with ID {dataset_id} to get")
            return None
        

    def get_metadata(self, dataset_id):
        """Return the dataset metadata, or None."""
        try: 
            entry = self._store[dataset_id]
        except KeyError:
            return None
        logger.debug(f"Got metadata for DataFrame with ID {dataset_id}")
        return {
            "id": entry["id"],
            "filename": entry["filename"],
            "rows": entry["rows"],
            "columns": entry["columns"],
            "column_names": entry["column_names"]
        }

    def update(self, dataset_id, df):
        """Replace an existing dataset; return True, or False if missing."""
        if dataset_id not in self._store:
            logger.debug(f"Failed to find a DataFrame with ID {dataset_id} to update")
            return False
        else:
            self._store[dataset_id] = [df, self._store[dataset_id][1]]
            logger.debug(f"Updated a DataFrame with ID {dataset_id}")
            return True

    def clear(self):
        """Clear all data and reset the ID counter."""
        self._store.clear()
        self._counter = 0
        logger.debug("Cleared data and reset ID counter to 0")
