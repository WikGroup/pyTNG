"""
Cosmological unit system for the ``pyTNG`` analysis package.
"""
from unyt.unit_registry import default_unit_registry,unyt_dims
from unyt.unit_object import Unit
from unyt import unyt_array,unyt_quantity
from sympy import Symbol, Rational
from unyt.equivalencies import Equivalence
import numpy as np
# Defining custom dimension

#: Dimension equivalent to the cosmological scale length (``unyt.dimension``).
a = Symbol("(scale_factor)", positive=True)
unyt_dims.base_dimensions.append(a)
a_unit = Unit(1*a,1.0,dimensions=a)

#: Dimension of co-moving length.
cm_length = unyt_dims.length/a

class CosmoEquivalence(Equivalence):

    type_name = "cosmology"
    _dims = (cm_length,unyt_dims.length)

    def _convert(self, x, new_dims,scale=1):

        if new_dims == unyt_dims.length:
            return np.multiply(x, scale, out=self._get_out(x))
        elif new_dims == cm_length:
            return np.true_divide(x, scale, out=self._get_out(x))

    def __str__(self):
        return "cosmological: scale-factor <-> unitless"

class CosmoUnits:
    """
    Unit class representing cosmological units.
    """
    _skipped_symbols = "%cm"

    def __init__(self,cosmology,z):
        """
        Initializes the :py:class:`units.cosmological.CosmoUnits`

        Parameters
        ----------
        cosmology: :py:class:`yt.utilities.cosmology.Cosmology`
            The cosmology to construct the cosmology from.
        """
        #: :py:class:`unyt.unit_registry.UnitRegistry` instance.
        self.registry = default_unit_registry
        self.registry.add("scale_factor",1.0,a)
        self.a_unit = Unit("scale_factor",1.0,dimensions=a,registry=self.registry)
        self.cosmology = cosmology
        self.z = z
        # constructing the co-moving coordinate names.
        _lut_names = list(self.registry.lut.keys())
        for unit_name in _lut_names:
            _s,_ud,_bv,_tex,_bool = self.registry.lut[unit_name]
            _new_ud = _ud.subs(unyt_dims.length,cm_length)

            if len(_tex):
                if _tex[-1] == "}":
                    _new_tex = _tex[:-1] + "cm}"
                else:
                    _new_tex = _tex + "_{\\rm{cm}}"
            else:
                _new_tex = ""

            self.registry.add(unit_name+"cm",_s,_new_ud,_new_tex,float(_bv),_bool)

        self._produce_unit_attributes()

    def _produce_unit_attributes(self):
        for unit_key,unit_data in self.registry.lut.items():
            if unit_key != "%cm":
                self.__setattr__(unit_key,Unit(unit_key,registry=self.registry))

    def array(self,value,units):
        """
        Create a :py:class:`unyt.array.unyt_array` instance with the given value and units.

        Parameters
        ----------
        value: array-like
            The array values to connect units to.
        units: str
            The units to assign.

        Returns
        -------
        :py:class:`unyt.array.unyt_array`

        """
        return unyt_array(value, units, registry=self.registry)
    def quantity(self,value,units):
        """
        Create a :py:class:`unyt.array.unyt_quantity` instance with the given value and units.

        Parameters
        ----------
        value: array-like
            The array values to connect units to.
        units: str
            The units to assign.

        Returns
        -------
        :py:class:`unyt.array.unyt_quantity`

        """
        return unyt_quantity(value, units, registry=self.registry)

    @staticmethod
    def _convert(dimension):
        return dimension.subs(cm_length,a*unyt_dims.length)



