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
    """
    Cosmological equivalence for conversion between comoving and physical coordinates.
    """
    type_name = "cosmology"
    _dims = (cm_length,unyt_dims.length) # we are converting length units in the various cosmological quantities.

    def _convert(self, x, new_dims,scale_factor=1):
        if new_dims == unyt_dims.length:
            return np.multiply(x, scale_factor, out=self._get_out(x))
        elif new_dims == cm_length:
            return np.true_divide(x, scale_factor, out=self._get_out(x))

    def __str__(self):
        return "cosmology: comoving dimension <-> physical dimension [function of a]"

class CosmoUnits:
    """
    Comoving units for a relevant scale.
    """
    _skipped_symbols = "%cm"

    def __init__(self,scale_factor,littleh):
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
        #: scale factor unit.
        self.a_unit = Unit("scale_factor",1.0,dimensions=a,registry=self.registry)
        #: the scale factor for this unit system.
        self.scale_factor = scale_factor
        self.littleh = littleh

        # Constructing comoving coordinates
        #==================================#
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

        # -- adding the little h unit -- #
        self.registry.add("h",base_value=self.littleh,dimensions=unyt_dims.dimensionless,tex_repr="h",offset=0.0,prefixable=False)
        # creating the attributes of the unit object
        #===========================================#
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




