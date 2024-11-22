from array import array
import math
import numpy as np


class Helpers:

    @staticmethod
    def shift4(arr, shift_positions: int, fill_value: float = np.nan) -> np.ndarray:
        """Shifts an array by num positions
        Can be used for right and left shift by using positive/negative value for num
        Inserted postions will have the value of fill_value
        Uses np.concatenate and np.full by chrisaycock

           Parameters
           ----------
           arr : sequence of array_like
               _description_
           shift_positions : int
               _description_
           fill_value : float, optional
               Fill shifted positions with this value, by default np.nan

           Returns
           -------
           ndarray
               The shifted array
        """
        if shift_positions == 0:
            return arr
        elif shift_positions >= 0:
            return np.concatenate(
                (np.full(shift_positions, fill_value), arr[:-shift_positions])
            )
        else:
            return np.concatenate(
                (arr[-shift_positions:], np.full(-shift_positions, fill_value))
            )

    @staticmethod
    def eng_string(x: float | int, format: str = "%s", si: bool = False) -> str:
        """Returns float/int value <x> formatted in a simplified engineering format -
        using an exponent that is a multiple of 3.
        format: printf-style string used to format the value before the exponent.
        si: if true, use SI suffix for exponent, e.g. k instead of e3, n instead of
        e-9 etc.

          Parameters
          ----------
          x : float, int
              _description_
          format : str, optional
              _description_, by default "%s"
          si : bool, optional
              _description_, by default False

          Returns
          -------
          str
              value <x> formatted in a simplified engineering format
        """

        sign = ""
        if x < 0:
            x = -x
            sign = "-"

        if x != 0:
            exp = int(math.floor(math.log10(x)))
        else:
            exp = 0

        exp3 = exp - (exp % 3)
        x3 = x / (10**exp3)

        if si and exp3 >= -24 and exp3 <= 24 and exp3 != 0:
            exp3_text = "yzafpnum kMGTPEZY"[int((exp3 - (-24)) / 3)]
        elif exp3 == 0:
            exp3_text = ""
        else:
            exp3_text = "e%s" % exp3

        return ("%s" + format + "%s") % (sign, x3, exp3_text)
