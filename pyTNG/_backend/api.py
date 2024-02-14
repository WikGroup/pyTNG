"""
API interaction code for the TNG simulation suite.
"""
import os
import pathlib as pt
import threading
from abc import ABC

import astropy.cosmology as cosmos
import numpy as np
import requests
from unyt import unyt_quantity

from pyTNG.units.cosmological import CosmoUnits
from pyTNG.utility.utils import EHalo, cgparams, devLogger, mylog, user_api_key

_user_header = {"api-key": user_api_key}

_levels = {
    0: "TNGSimulationAPI",
    1: "TNGSnapshotAPI",
    2: "TNGSubhaloAPI",
}

available_cosmologies = {
    "WMAP-1": cosmos.WMAP1,
    "WMAP-3": cosmos.WMAP3,
    "WMAP-5": cosmos.WMAP5,
    "WMAP-7": cosmos.WMAP7,
    "WMAP-9": cosmos.WMAP9,
    "Planck2013": cosmos.Planck13,
    "Plank2015": cosmos.Planck15,
    "Plank2018": cosmos.Planck18,
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
    Abstract base class representation of a TNG API call.
    """

    #: base url to gain api access.
    root_api_url = cgparams["TNG"]["base_url"]
    _level = None

    def __new__(cls, **kwargs):
        _subclass_dict = {k.__name__: k for k in TNGAPI.__subclasses__()}

        if len(kwargs) - 1 == cls._level:
            return object.__new__(cls)

        else:
            return object.__new__(_subclass_dict[_levels[len(kwargs) - 1]])

    def __init__(self, *args, **kwargs):
        #: The name of this API object.
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

    def __getattr__(self, item):
        if hasattr(super(), item):
            return super().__getattribute__(item)

        elif item in self.attributes:
            return self.attributes[item]
        else:
            raise AttributeError(f"The attribute {item} was not found.")

    @property
    def meta(self):
        """
        The meta data associated with the API call for this object.
        """
        return self._meta

    @property
    def attributes(self):
        """
        The specific attributes of the API call.
        """
        if self._has_called is False:
            # we haven't called to the API yet.
            self.call()

        return self._attr

    @property
    def api_url(self):
        """
        The call URL for the API access object.
        """
        return self._base_api_url

    def call(self, directory=None, **kwargs):
        """
        Calls the API.

        Parameters
        ----------
        directory: str
            The directory to save any downloadable objects from the call to.
        **kwargs:
            Optional kwargs to pass to the API settings.

        Returns
        -------
        dict
            The attribute dictionary. Equivalent to ``self.attributes``.

        """
        status, self._attr = _api_fetch(self.api_url, directory=directory, **kwargs)
        self._has_called = True
        return self._attr

    @property
    def available_files(self):
        """
        Available downloadable objects in this API call.
        """
        if "files" in self.attributes:
            return self.attributes["files"]
        else:
            return {}

    @property
    def available_vis(self):
        """
        Available visualization files in the API call.
        """
        if "vis" in self.attributes:
            return self.attributes["vis"]
        else:
            return {}

    def image(self, obj, ax=None, fig=None, **kwargs):
        """
        Render a viewable image from the API through :py:mod:`matplotlib`.

        Parameters
        ----------
        obj: str
            The object key (from :py:attr:`TNGAPI.available_vis`) corresponding to the desired visualization file.
        ax: :py:class:`matplotlib.axes.Axes`, optional
            The axes to attach the figure to. If ``None``, then one is created.
        fig: py:class:`matplotlib.axes.Figure`, optional
            The figure to attach the figure to. If ``None``, then one is created.
        kwargs: optional
            Additional kwargs to pass directly to :py:func:`matplotlib.pyplot.imshow`.

        Returns
        -------
        fig
            The figure containing the image.
        axes
            The axes containing the image.
        """
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
    """
    :py:class:`_backend.api.TNGAPI` object representation of a complete simulation API reference.
    """

    _level = 0

    def __init__(self, simulation=None):
        """
        Initializes the :py:class:`_backend.api.TNGSimulationAPI` object.

        Parameters
        ----------
        simulation: str
            The name of the simulation to load.
        """
        super().__init__()
        mylog.info(f"Loading API object [{simulation}].")
        #: the name of the API
        self.name = simulation
        self.cosmology = available_cosmologies[self.attributes["cosmology"]]
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
        """Parent simulations of this simulation."""
        return self.attributes["parent_simulation"]

    @property
    def children(self):
        """Child simulations of this simulation."""
        return self.attributes["child_simulation"]

    @property
    def snapshots(self):
        """Available snapshots for this simulation."""
        if not self._has_called_snapshots:
            status, self._snapshots = _api_fetch(
                self.attributes["snapshots"], directory=None
            )
            self._has_called_snapshots = True
        return self._snapshots


class TNGSnapshotAPI(TNGAPI):
    """
    :py:class:`_backend.api.TNGAPI` object representation of a snapshot API reference.
    """

    _level = 1

    def __init__(self, simulation=None, snapshot=None):
        """
        Initializes the :py:class:`_backend.api.TNGSnapshotAPI` object.

        Parameters
        ----------
        simulation: str
            The name of the simulation to load.
        snapshot: int
            The snapshot number to load.
        """
        #: the name of the API
        super().__init__()
        mylog.info(f"Loading API object [{simulation} - {snapshot}].")
        self.name = snapshot
        self.simulation = simulation
        self.snapshot = snapshot

        # Meta Data
        # ----------#
        self._meta = {
            "simulation": _api_fetch(super().root_api_url + f"/{self.simulation}/")[1],
            "snapshot": snapshot,
        }
        self._base_api_url = (
            super().root_api_url + f"/{self.simulation}/" + f"snapshots/{self.name}/"
        )

        # Cosmological management
        # ------------------------#
        self.cosmology = available_cosmologies[self.meta["simulation"]["cosmology"]]
        self.z = self.redshift
        self.scale_factor = self.cosmology.scale_factor(self.z)
        self.units = CosmoUnits(self.scale_factor, self.cosmology.h)
        #: flags
        self._has_called = False

    @property
    def parents(self):
        """Simulation in which this snapshot is a child."""
        return self.simulation


class TNGSubhaloAPI(TNGAPI):
    """
    :py:class:`_backend.api.TNGAPI` object representation of a subhalo API reference.
    """

    _level = 2

    def __init__(self, simulation=None, snapshot=None, subhalo=None):
        """
        Initializes the :py:class:`_backend.api.TNGsubhaloAPI` object.

        Parameters
        ----------
        simulation: str
            The name of the simulation to load.
        snapshot: int
            The snapshot number to load.
        subhalo: int
            The subhalo number to load.
        """
        #: the name of the API
        super().__init__(self)
        mylog.info(f"Loading API object [{simulation}-{snapshot}-{subhalo}].")
        self.name = snapshot
        self.simulation = simulation
        self.snapshot = snapshot
        self.subhalo = subhalo

        #: metadata
        self._meta = {
            "simulation": _api_fetch(super().root_api_url + f"/{self.simulation}/")[1],
            "snapshot": _api_fetch(
                super().root_api_url
                + f"/{self.simulation}/"
                + f"snapshots/{self.name}/"
            )[1],
            "subhalo": subhalo,
        }
        self._base_api_url = (
            super().root_api_url
            + f"/{self.simulation}/"
            + f"snapshots/{self.name}/"
            + f"subhalos/{self.subhalo}"
        )

        # Cosmological management
        # ------------------------#
        self.cosmology = available_cosmologies[self._meta["simulation"]["cosmology"]]
        self.z = self._meta["snapshot"]["redshift"]
        self.scale_factor = self.cosmology.scale_factor(self.z)
        self.units = CosmoUnits(self.scale_factor, self.cosmology.h)

        # flags
        self._has_called = False

    @property
    def parents(self):
        """Access to the parent snapshot."""
        return self.attributes["snap"]

    @property
    def center_of_mass(self):
        return self.units.array([self.cm_x, self.cm_y, self.cm_z], "kpccm/h")

    @property
    def center(self):
        return self.units.array([self.pos_x, self.pos_y, self.pos_z], "kpccm/h")

    @property
    def peculiar_velocity(self):
        return self.units.array([self.vel_x, self.vel_y, self.vel_z], "km/s")

    @property
    def velocity_dispersion_3d(self):
        return self.units.quantity(np.sqrt(3) * self.veldisp, "km/s")

    @property
    def spin(self):
        return self.units.array(
            [self.spin_x, self.spin_y, self.spin_z], "(kpc/h)*(km/s)"
        )

    @property
    def star_formation_rate(self):
        return self.units.quantity(self.sfr, "Msun/yr")

    @property
    def mass(self):
        return unyt_quantity(10 ** (self.mass_log_msun), "Msun")

    def download(self, filename, grab_parent=False, **kwargs):
        return download_cutout(
            self.simulation,
            self.snapshot,
            self.subhalo,
            filename,
            grab_parent=grab_parent,
            **kwargs,
        )


def download_cutout(
    simulation, snapshot, subhalo, filename, grab_parent=False, **kwargs
):
    """
    Downloads the TNG cutout of the specified subhalo.

    Parameters
    ----------
    simulation: str
        The name of the simulation to pull from.
    snapshot: int
        The snapshot number.
    subhalo: int
        The subhalo id.
    filename: str
        The filename at which to save the cutout.
    grab_parent: bool, optional
        If ``True``, the function will iteratively seek out a parent halo until it finds the central halo of the system.

    Returns
    -------

    """
    base_url = (
        TNGAPI.root_api_url
        + f"/{simulation}/"
        + f"snapshots/{snapshot}/"
        + f"subhalos/{subhalo}"
    )

    _, meta = _api_fetch(base_url)

    call_url = (
        meta["cutouts"]["subhalo"]
        if not grab_parent
        else meta["cutouts"]["parent_halo"]
    )
    with EHalo(text=f"Downloading {simulation}-{snapshot}-{subhalo} [{call_url}]"):
        devLogger.debug(
            f"Calling {call_url} [Thread={threading.current_thread().name}]."
        )
        r = requests.get(call_url, params=kwargs, headers=_user_header)
        r.raise_for_status()

        with open(filename, "wb") as f:
            f.write(r.content)

    return filename


def download_snapshot():
    pass


if __name__ == "__main__":
    q = TNGSubhaloAPI(simulation="Illustris-3", snapshot=75, subhalo=2)
    q.download("test.hdf5", grab_parent=False)
