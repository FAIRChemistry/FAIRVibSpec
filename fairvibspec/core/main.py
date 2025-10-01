from datetime import datetime

from fairvibspec.core.fairvibspec import FAIRVibSpec as FAIRVibSpecRoot


class FAIRVibSpec:
    def __init__(self):
        self._data_model = None
        self._init_data_model()

    def _init_data_model(self):
        self.data_model = FAIRVibSpecRoot(
            datetime_created=datetime.now().isoformat(),
        )

    @property
    def data_model(self):
        return self._data_model

    @data_model.setter
    def data_model(self, data_model: "FAIRVibSpec"):
        if data_model is None:
            self._data_model = None
            return
        if not isinstance(data_model, FAIRVibSpecRoot):
            raise ValueError(
                "data_model must be a FAIRVibSpec data model object"
            )
        self._data_model = data_model
        if not self._data_model.datetime_created:
            self._data_model.datetime_created = datetime.now().isoformat()
        self._data_model.datetime_modified = datetime.now().isoformat()

    @data_model.deleter
    def data_model(self):
        self._data_model = None
