from tfi.tensor.frame import TensorFrame as _TensorFrame
from tfi.tensor.codec import encode as _encode_tensor
from tfi.base import _recursive_transform

from collections import OrderedDict as _OrderedDict
import base64
import numpy as np

import json

_ACCEPT_MIMETYPES = _OrderedDict([
  ("image/png", lambda x: {
    '$base64': base64.b64encode(x).decode('utf-8'),
    '$mimetype': 'image/png',
  }),
  ("image/jpeg", lambda x: {
    '$base64': base64.b64encode(x).decode('utf-8'),
    '$mimetype': 'image/jpeg',
  }),
  # "text/plain": lambda x: x,
])

_TRANSFORMS = {}

def _encode_transformed_tensor_value(o):
  t = type(o)
  if t in _TRANSFORMS:
    o = _TRANSFORMS[t](o)

  return _encode_tensor(_ACCEPT_MIMETYPES, o)


# Use python/jsonable so we to a recursive transform before jsonification.
_ACCEPT_MIMETYPES["python/jsonable"] = _encode_transformed_tensor_value


def as_jsonable(result):
  r = _recursive_transform(result, _encode_transformed_tensor_value)
  if r is not None:
    return r
  return result


_TRANSFORMS[_TensorFrame] = lambda o: _TensorFrame(
      *[
        (shape, name, _recursive_transform(tensor, _encode_transformed_tensor_value))
        for shape, name, tensor in o.tuples()
      ],
      **o.shape_labels(),
    ).zipped()

_TRANSFORMS[np.int32] = lambda o: int(o)

try:
  import pandas as _pandas

  def df_to_dict(df):
    d = df.to_dict('split')
    del d['index']
    return d
  _TRANSFORMS[_pandas.DataFrame] = df_to_dict
except ImportError:
  pass

try:
  import pyarrow as _pyarrow
  _TRANSFORMS[_pyarrow.lib.Buffer] = lambda o: base64.b64encode(o.to_pybytes()).decode('utf-8')
except ImportError:
  pass
