"""
API interaction code for the TNG simulation suite.
"""
import os
import pathlib as pt
import threading
from abc import ABC
import unyt as u
from unyt import unyt_array,unyt_quantity
import requests

from pyTNG.utility.utils import EHalo, cgparams, devLogger, mylog, user_api_key


_user_header = {"api-key": user_api_key}

_levels = {
    0: "TNGSimulationAPI",
    1: "TNGSnapshotAPI",
    2: "TNGSubhaloAPI",
}




def _api_fetch(url, directory=None, **kwargs):
    # fetches the requisite data from the API.
    with EHalo(text=f"Fetching from {url}..."):
        devLogger.debug(f"Calling {url} [Thread={threading.current_thread().name}].")

        r = requests.get(url, params=kwargs, headers=_user_header)
        r.raise_for_status()

        if r.headers["content-type"] == "application/json":
            return 0, r.json()  # parse json responses automatically

        if "content-disposition" in r.headers:
            filename = r.headers["content-disposition"].split("filename=")[1]

            if directory is not None:
                if not os.path.exists(directory):
                    pt.Path(directory).mkdir(
                        parents=True, exist_ok=True
                    )  # we keep exist_ok to prevent race condition errors.

                with open(filename, "wb") as f:
                    f.write(r.content)
                return 2, filename  # return the filename string
            else:
                return 2, r
        return 1, r


class TNGAPI(ABC):
    """
    User base class for interactions with the TNG API.
    """

    #: The url to access the main TNG api.
    root_api_url = cgparams["TNG"]["base_url"]
    _level = None

    def __new__(cls, **kwargs):
        _subclass_dict = {k.__name__: k for k in TNGAPI.__subclasses__()}

        if len(kwargs)-1 == cls._level:
            return object.__new__(cls)

        else:
            return object.__new__(_subclass_dict[_levels[len(kwargs)-1]])


    def __init__(self, *args, **kwargs):
        self.name = None
        self._base_api_url = None
        self._attr = None
        self._meta = None

        # flags
        self._has_called = False

    def __str__(self):
        return f"<{self.__class__.__name__}> [name={self.name}]"

    def __repr__(self):
        return self.__str__()

    @property
    def meta(self):
        return self._meta

    @property
    def attributes(self):
        if self._has_called is False:
            # we haven't called to the API yet.
            self.call()

        return self._attr

    @property
    def api_url(self):
        return self._base_api_url

    def call(self, directory=None, **kwargs):
        status, self._attr = _api_fetch(self.api_url, directory=directory, **kwargs)
        self._has_called = True
        return self._attr

    @property
    def available_files(self):
        if "files" in self.attributes:
            return self.attributes["files"]
        else:
            return {}

    @property
    def available_vis(self):
        if "vis" in self.attributes:
            return self.attributes["vis"]
        else:
            return {}

    def image(self, obj, ax=None, fig=None, **kwargs):
        mylog.info(f"Fetching image {obj} from {self.__str__()}.")
        from io import BytesIO

        import matplotlib.image as mpimg
        import matplotlib.pyplot as plt

        if obj not in self.available_vis:
            raise ValueError(f"The object {obj} is not available in {self.__str__()}.")

        obj_url = self.available_vis[obj]

        try:
            status, data = _api_fetch(obj_url)
        except requests.exceptions.HTTPError as http_exp:
            mylog.warning(
                f"Attempt to fetch {obj} from {self} caused HTTP error: {http_exp.__str__()}"
            )
            return None

        if not fig:
            fig = plt.figure(figsize=(10, 10))
            fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        if not ax:
            ax = fig.add_subplot(111)

        file_object = BytesIO(data.content)
        ax.axes.get_xaxis().set_ticks([])
        ax.axes.get_yaxis().set_ticks([])
        ax.axis("off")
        ax.imshow(mpimg.imread(file_object), **kwargs)

        return fig, ax


class TNGSimulationAPI(TNGAPI):
    _level = 0

    def __init__(self, simulation=None):
        #: the name of the API
        super().__init__()
        mylog.info(f"Loading API object [{simulation}].")
        self.name = simulation
        #: metadata
        self._meta = {"simulation": simulation}
        self._base_api_url = TNGAPI.root_api_url + f"/{self.name}/"
        self._attr = None
        self._snapshots = None
        # flags
        self._has_called = False
        self._has_called_snapshots = False

    @property
    def parents(self):
        return self.attributes["parent_simulation"]

    @property
    def children(self):
        return self.attributes["child_simulation"]

    @property
    def snapshots(self):
        if not self._has_called_snapshots:
            status, self._snapshots = _api_fetch(
                self.attributes["snapshots"], directory=None
            )
            self._has_called_snapshots = True
        return self._snapshots


class TNGSnapshotAPI(TNGAPI):
    _level = 1

    def __init__(self, simulation=None, snapshot=None):
        #: the name of the API
        super().__init__()
        mylog.info(f"Loading API object [{simulation} - {snapshot}].")
        self.name = snapshot
        self.simulation = simulation
        self.snapshot = snapshot

        #: metadata
        self._meta = {"simulation": simulation, "snapshot": snapshot}
        self._base_api_url = (
            super().root_api_url + f"/{self.simulation}/" + f"snapshots/{self.name}/"
        )

        # flags
        self._has_called = False

    @property
    def parents(self):
        return self.simulation


class TNGSubhaloAPI(TNGAPI):
    _level = 2

    def __init__(self, simulation=None, snapshot=None, subhalo=None):
        #: the name of the API
        super().__init__(self)
        mylog.info(f"Loading API object [{simulation}-{snapshot}-{subhalo}].")
        self.name = snapshot
        self.simulation = simulation
        self.snapshot = snapshot
        self.subhalo = subhalo
        #: metadata
        self._meta = {
            "simulation": simulation,
            "snapshot": snapshot,
            "subhalo": subhalo,
        }
        self._base_api_url = (
            super().root_api_url
            + f"/{self.simulation}/"
            + f"snapshots/{self.name}/"
            + f"subhalos/{self.subhalo}"
        )

        # flags
        self._has_called = False

    @property
    def parents(self):
        return self.attributes["snap"]

    @property
    def center(self):
        unyt_array([self.attributes['cm_x'],
                    self.attributes['cm_y'],
                    self.attributes['cm_z']],u.kpccm/u.h)




