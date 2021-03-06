# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import

import math

from numba.typesystem import *
from numba.typesystem.itypesystem import nbo

import numpy as np

def map_dtype(dtype):
    """
    Map a NumPy dtype to a minitype.

    >>> map_dtype(np.dtype(np.int32))
    int32
    >>> map_dtype(np.dtype(np.int64))
    int64
    >>> map_dtype(np.dtype(np.object))
    PyObject *
    >>> map_dtype(np.dtype(np.float64))
    float64
    >>> map_dtype(np.dtype(np.complex128))
    complex128
    """
    if dtype.byteorder not in ('=', nbo, '|') and dtype.kind in ('iufbc'):
        raise minierror.UnmappableTypeError(
                "Only native byteorder is supported", dtype)

    item_idx = int(math.log(dtype.itemsize, 2))
    if dtype.kind == 'i':
        return [int8, int16, int32, int64][item_idx]
    elif dtype.kind == 'u':
        return [uint8, uint16, uint32, uint64][item_idx]
    elif dtype.kind == 'f':
        if dtype.itemsize == 2:
            pass # half floats not supported yet
        elif dtype.itemsize == 4:
            return float32
        elif dtype.itemsize == 8:
            return float64
        elif dtype.itemsize == 16:
            return float128
    elif dtype.kind == 'b':
        return int8
    elif dtype.kind == 'c':
        if dtype.itemsize == 8:
            return complex64
        elif dtype.itemsize == 16:
            return complex128
        elif dtype.itemsize == 32:
            return complex256
    elif dtype.kind == 'V':
        fields = [(name, map_dtype(dtype.fields[name][0]))
                      for name in dtype.names]
        is_aligned = dtype.alignment != 1
        return struct_(fields, packed=not getattr(dtype, 'isalignedstruct',
                                                  is_aligned))
    elif dtype.kind == 'O':
        return object_

typemap = {
    int8     : np.int8,
    int16    : np.int16,
    int32    : np.int32,
    int64    : np.int64,
    uint8    : np.uint8,
    uint16   : np.uint16,
    uint32   : np.uint32,
    uint64   : np.uint64,

    float_   : np.float32,
    double   : np.float64,
    longdouble: np.longdouble,

    short    : np.dtype('h'),
    int_     : np.dtype('i'),
    long_    : np.dtype('l'),
    longlong : np.longlong,
    ushort   : np.dtype('H'),
    uint     : np.dtype('I'),
    ulong    : np.dtype('L'),
    ulonglong: np.ulonglong,

    complex64: np.complex64,
    complex128: np.complex128,
    complex256: getattr(np, 'complex256', None),

    bool_    : np.bool,
    object_  : np.object,
}
typemap = dict((k, np.dtype(v)) for k, v in typemap.iteritems())

def to_dtype(type):
    if type.is_struct:
        fields = [(field_name, to_dtype(field_type))
                      for field_name, field_type in type.fields]
        return np.dtype(fields, align=not type.packed)
    elif type.is_array and type.ndim == 1:
        return to_dtype(type.dtype)
    elif type in typemap:
        return typemap[type]
    elif type.is_int:
        name = 'int' if type.signed else 'uint'
        return np.dtype(getattr(np, name + str(type.itemsize * 8)))
    else:
        raise ValueError("Cannot convert '%s' to numpy type" % (type,))