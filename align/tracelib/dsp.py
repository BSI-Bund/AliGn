import numpy as np
from numba import njit
from scipy.signal import lfilter

## split the trace into intervals of size intervalSize
## and


def calculateVariance(trace, intervalSize):
    """
    split the trace into intervals of size intervalSize
    and calculate the signal variance for each interval
    if (trace % intervalSize) is not zero, the last
    interval (smaller than intervalSize) is ignored
    :param trace: the input trace
    :param intervalSize: must be smaller than trace length
    :return: an np.array containing the signal variance
    """
    if intervalSize >= len(trace):
        raise ValueError("calculateVariance: intervalSize larger than trace length.")
    trace = np.array(trace)
    remove_end = len(trace) % intervalSize
    if remove_end != 0:
        trace = trace[:-remove_end]
    res = []
    chunks = trace.reshape(-1, intervalSize)
    x = chunks.shape[0]
    for i in range(0, x):
        v = np.var(chunks[i, :])
        res.append(v)
    return np.array(res)


def findMinimum(trace, range_start, range_stop, threshold, verbose=False):
    x = np.argmin(trace[range_start:range_stop])
    if verbose:
        print("findMinimum: x: {}".format(x))
    minimum = trace[range_start:range_stop][x]
    if verbose:
        print("findMinimum: minimum: {}".format(minimum))
    if minimum < threshold:
        return (x + range_start, minimum)
    else:
        return None


def findMaximum(trace, range_start, range_stop, threshold):
    x = np.argmax(trace[range_start:range_stop])
    maximum = trace[range_start:range_stop][x]
    if maximum > threshold:
        return (x + range_start, maximum)
    else:
        return None


def matchRisingEdge(trace, offset, threshold):
    x = np.argmax(trace[offset:] > threshold)
    if x != 0:
        x += offset
    return x


def matchFallingEdge(trace, offset, threshold):
    x = np.argmax(trace[offset:] < threshold)
    if x != 0:
        x += offset
    return x


# match a structure akin to
#   _______
# _|       \___
@njit
def matchUpperWidth(trace, offset, width, threshold):
    for i in range(offset, len(trace) - width - 1):
        if not (np.any(trace[i + offset : i + offset + width] <= threshold)):
            return i + offset
    return 0


# match a structure akin to
# __        ___
#   \______/
@njit
def matchLowerWidth(trace, offset, width, threshold):
    for i in range(offset, len(trace) - width - 1):
        if not (np.any(trace[i + offset : i + offset + width] >= threshold)):
            return i + offset
    return 0


@njit
def computeCorrcoef(vec_a, vec_b):
    return np.corrcoef(vec_a, vec_b)[0][1]


## compresses a trace by averaging chunks of a trace
## of size interval. If the trace does not divide
## by interval, the last chunk is disregarded
## This is very slow due to the non-accelerated
## loop; using numba (cf below) is much faster,
def compress_trace(trace, interval):
    l = len(trace)
    new_len = np.int(l / interval)
    comb_x = np.zeros(new_len, dtype=np.float)
    j = 0
    for i in range(0, new_len * interval, interval):
        summe = np.mean(trace[i : i + interval])
        comb_x[j] = summe
        j += 1
    return comb_x


def frange(start, stop, step=1.0):
    while start < stop:
        yield start
        start += step


def _gauss(x):
    return np.exp(-(x**2.0) / 2.0) / (np.sqrt(2 * np.pi))


_gauss_vals = np.array(list(frange(-4.0, 4.2, 0.2)))

_gaussfilt = _gauss(_gauss_vals) * 0.2


def gaussFilter(trace):
    return lfilter(_gaussfilt, 1, trace)


@njit
def count_nonzero_jit(vec):
    s = 0
    for i in vec:
        if i != 0:
            s += 1
    return s


@njit
def matchByCorrelation(trace, pattern, start, stop, stepSize=1):
    coeffs = []
    lp = len(pattern)
    for i in range(start, stop - len(pattern), stepSize):
        if count_nonzero_jit(trace[i : i + lp]) > 0:
            coeffs.append(computeCorrcoef(trace[i : i + lp], pattern))
        else:
            coeffs.append(0.0)
    offset = np.argmax(np.array(coeffs)) + (start)
    corrValue = np.amax(np.array(coeffs))
    return (offset, corrValue)


@njit
def matchBySosd(trace, pattern, start, stop, stepSize=1):
    diffs = []
    lp = len(pattern)
    for i in range(start, stop - len(pattern), stepSize):
        d = np.sum((trace[i : i + lp] - pattern) ** 2)
        diffs.append(d)
    offset = np.argmin(np.array(diffs)) + (start)
    diffVal = np.amin(np.array(diffs))
    return (offset, diffVal)


def shiftTrace(trace, shiftValue, fill_value=0):
    """
    :param trace: Input trace (to shift)
    :param shiftValue: positive (shift to right) or negative (shift to left) value
    :param fill_value: fill missing values with this value. default 0.
    :return:
    """
    result = np.empty_like(trace)
    if shiftValue > 0:
        result[:shiftValue] = fill_value
        result[shiftValue:] = trace[:-shiftValue]
    elif shiftValue < 0:
        result[shiftValue:] = fill_value
        result[:shiftValue] = trace[-shiftValue:]
    else:
        result = trace
    return result


# taken from PyAstronomy
def smooth(x, windowLen, window="flat"):
    """
    Smooth data using a window function.

    This method is based on the convolution of a window function with the signal.
    The window function is normalized so that the sum of its entries amounts to
    one. The signal is prepared by adding reflected copies of the signal
    (with the window size) to both ends of the input array, so that the output
    array can have the same length as the input. Consequently the smoothing at
    the edges is actually based on extrapolation.

    .. note:: This algorithm was adopted from the scipy cookbook
              (http://www.scipy.org/Cookbook/SignalSmooth). The copyright
              of the original algorithm belongs to the authors of that
              cookbook algorithm.

    Parameters
    ----------
    x : array
        The input signal
    windowLen : int
        The dimension of the smoothing window. It must be an odd integer.
    window : string, {'flat', 'hanning', 'hamming', 'bartlett', 'blackman'}
        The window function to be used. A flat window will
        produce a moving average smoothing.

    Returns
    -------
    Smoothed signal : array
        The smoothed signal. Same length as input array.
    """

    if x.ndim != 1:
        raise (
            ValueError(
                "Only one dimensional arrays can be smoothed. Dimension of "
                + "given array is "
                + str(x.ndim),
                solution="Change dimension of input.",
            )
        )

    if x.size < windowLen:
        raise (
            ValueError(
                "Input vector needs to be bigger than window size.",
                solution="Check the length of the input array and window size.",
            )
        )

    if windowLen < 3:
        # PE.warn(PE.PyAValError("Length of window is smaller then 3. No smoothing is done.",
        #                       solution="Check window size."))
        return x

    if windowLen % 2 != 1:
        raise (ValueError("Parameter `windowLen` should be an odd integer"))

    # Extend input array at the edges to have the same
    # length for the output array. Insert a mirrored version
    # of the first part of the data array in front of the
    # first data point; apply the same scheme to the end of the
    # data array.
    s = np.r_[x[windowLen - 1 : 0 : -1], x, x[-1:-windowLen:-1]]

    if window == "flat":
        # This is a moving average
        w = np.ones(windowLen, "d")
    elif window == "hanning":
        w = np.hanning(windowLen)
    elif window == "hamming":
        w = np.hamming(windowLen)
    elif window == "bartlett":
        w = np.bartlett(windowLen)
    elif window == "blackman":
        w = np.blackman(windowLen)
    else:
        raise (
            ValueError(
                "Current `window` parameter ("
                + str(window)
                + ") is not supported. "
                + "Must be one of: 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'",
                solution="Choose one of the above window types.",
            )
        )

    y = np.convolve(w / w.sum(), s, mode="valid")
    return y[(windowLen // 2) : -(windowLen // 2)]


@njit
def findGaps(trace, threshold, positive=True):
    _len = len(trace)
    _begin = 0
    _end = 0
    hasGap = False
    i = 0
    gaps = []
    while i < _len:
        if positive and trace[i] < threshold:
            _begin = i
            _end = i
            j = i + 1
            while j < _len:
                if trace[j] < threshold:
                    _end = j
                    j += 1
                else:
                    gaps.append([_begin, _end])
                    break
            if j == _len:
                if _end == (j - 1):
                    gaps.append([_begin, _end])
                break
            i = j + 1
        elif not positive and trace[i] > threshold:
            _begin = i
            _end = i
            j = i + 1
            while j < _len:
                if trace[j] > threshold:
                    _end = j
                    j += 1
                else:
                    gaps.append([_begin, _end])
                    break
            if j == _len:
                if _end == (j - 1):
                    gaps.append([_begin, _end])
                break
            i = j + 1
        else:
            i += 1
    if len(gaps) > 0:
        return gaps
    else:
        return None


@njit
def findLargestGap(trace, threshold, positive=True):
    gaps = findGaps(trace, threshold=threshold, positive=positive)
    if gaps is None:
        return None
    largest = 0
    length = 0
    for iGap, gap in enumerate(gaps):
        if (gap[1] - gap[0]) > length:
            length = gap[1] - gap[0]
            largest = iGap
    return gaps[largest]


# dkl: was macht diese Funktion? Wird hier nicht einfach nur die Trace von
# links nach rechts durchgegangen, und geschaut wann das letzte mal ein
# wert über threshold existiert?
@njit
def findFirstPeak(trace, minDist=10, threshold=None, findMax=True):
    hasPeak = False
    peakPos = 0
    i = 0
    while i < len(trace):
        if findMax and trace[i] > trace[peakPos]:
            if threshold is None or trace[i] >= threshold:
                hasPeak = True
                peakPos = i
        elif not findMax and trace[i] < trace[peakPos]:
            if threshold is None or trace[i] <= threshold:
                hasPeak = True
                peakPos = i
        else:
            if hasPeak and (i - peakPos) > minDist:
                break
        i += 1

    if not hasPeak:
        return None
    else:
        return [peakPos, trace[peakPos]]


@njit
def findLastPeak(trace, minDist=10, threshold=None, findMax=True):
    peak = findFirstPeak(
        trace[::-1], minDist=minDist, threshold=threshold, findMax=findMax
    )
    if not peak is None:
        peak[0] = len(trace) - 1 - peak[0]
    return peak


def findPeaks(
    x, minDist, threshold=None, findMax=True, thresholdMin=None, findMin=False
):
    peaks = []
    if findMax:
        i = 0
        while i < len(x):
            if not threshold is None and not x[i] > threshold:
                i += 1
                continue
            ## search right
            ismax = True
            for iR in range(1, minDist):
                if (i + iR) < len(x) and x[i + iR] > x[i]:
                    ismax = False
                    i = i + iR
                    break

            ## search left
            if ismax:
                for iR in range(1, minDist):
                    if (i - iR) >= 0 and x[i - iR] > x[i]:
                        ismax = False
                        i += 1
                        break
            if ismax:
                if not i == len(x) - 1 and not i == 0:
                    peaks.append((i, x[i]))
                i += minDist

    if findMin:
        i = len(x) - 1
        while i >= 0:
            if not thresholdMin is None and not x[i] < threshold:
                i -= 1
                continue
            ## search left
            ismin = True
            for iL in range(1, minDist):
                if (i - iL) >= 0 and x[i - iL] < x[i]:
                    ismin = False
                    i = i - iL
                    break

            ## search right
            if ismin:
                for iL in range(1, minDist):
                    if (i + iL) < len(x) and x[i + iL] < x[i]:
                        ismin = False
                        i -= 1
                        break
            if ismin:
                if not i == 0 and not i == len(x) - 1:
                    peaks.append((i, x[i]))
                i -= minDist

    return np.asanyarray(peaks)


def _plot(x, mph, mpd, threshold, edge, valley, ax, ind):
    """Plot results of the detect_peaks function, see its help."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not available.")
    else:
        if ax is None:
            _, ax = plt.subplots(1, 1, figsize=(8, 4))

        ax.plot(x, "b", lw=1)
        if ind.size:
            label = "valley" if valley else "peak"
            label = label + "s" if ind.size > 1 else label
            ax.plot(
                ind,
                x[ind],
                "+",
                mfc=None,
                mec="r",
                mew=2,
                ms=8,
                label="%d %s" % (ind.size, label),
            )
            ax.legend(loc="best", framealpha=0.5, numpoints=1)
        ax.set_xlim(-0.02 * x.size, x.size * 1.02 - 1)
        ymin, ymax = x[np.isfinite(x)].min(), x[np.isfinite(x)].max()
        yrange = ymax - ymin if ymax > ymin else 1
        ax.set_ylim(ymin - 0.1 * yrange, ymax + 0.1 * yrange)
        ax.set_xlabel("Data #", fontsize=14)
        ax.set_ylabel("Amplitude", fontsize=14)
        mode = "Valley detection" if valley else "Peak detection"
        ax.set_title(
            "%s (mph=%s, mpd=%d, threshold=%s, edge='%s')"
            % (mode, str(mph), mpd, str(threshold), edge)
        )
        # plt.grid()
        plt.show()


def detectPeaks(
    x,
    mph=None,
    mpd=1,
    threshold=0,
    edge="rising",
    kpsh=False,
    valley=False,
    show=False,
    ax=None,
):
    """Detect peaks in data based on their amplitude and other features.

    Parameters
    ----------
    x : 1D array_like
        data.
    mph : {None, number}, optional (default = None)
        detect peaks that are greater than minimum peak height.
    mpd : positive integer, optional (default = 1)
        detect peaks that are at least separated by minimum peak distance (in
        number of data).
    threshold : positive number, optional (default = 0)
        detect peaks (valleys) that are greater (smaller) than `threshold`
        in relation to their immediate neighbors.
    edge : {None, 'rising', 'falling', 'both'}, optional (default = 'rising')
        for a flat peak, keep only the rising edge ('rising'), only the
        falling edge ('falling'), both edges ('both'), or don't detect a
        flat peak (None).
    kpsh : bool, optional (default = False)
        keep peaks with same height even if they are closer than `mpd`.
    valley : bool, optional (default = False)
        if True (1), detect valleys (local minima) instead of peaks.
    show : bool, optional (default = False)
        if True (1), plot data in matplotlib figure.
    ax : a matplotlib.axes.Axes instance, optional (default = None).

    Returns
    -------
    ind : 1D array_like
        indeces of the peaks in `x`.

    Notes
    -----
    The detection of valleys instead of peaks is performed internally by simply
    negating the data: `ind_valleys = detect_peaks(-x)`

    The function can handle NaN's

    See this IPython Notebook [1]_.

    References
    ----------
    .. [1] http://nbviewer.ipython.org/github/demotu/BMC/blob/master/notebooks/DetectPeaks.ipynb

    Examples
    --------
    >>> from align.tracelib.dsp import detectPeaks
    >>> x = np.random.randn(100)
    >>> x[60:81] = np.nan
    >>> # detect all peaks and plot data
    >>> ind = detectPeaks(x, show=True)
    >>> print(ind)

    >>> x = np.sin(2*np.pi*5*np.linspace(0, 1, 200)) + np.random.randn(200)/5
    >>> # set minimum peak height = 0 and minimum peak distance = 20
    >>> detectPeaks(x, mph=0, mpd=20, show=True)

    >>> x = [0, 1, 0, 2, 0, 3, 0, 2, 0, 1, 0]
    >>> # set minimum peak distance = 2
    >>> detectPeaks(x, mpd=2, show=True)

    >>> x = np.sin(2*np.pi*5*np.linspace(0, 1, 200)) + np.random.randn(200)/5
    >>> # detection of valleys instead of peaks
    >>> detectPeaks(x, mph=0, mpd=20, valley=True, show=True)

    >>> x = [0, 1, 1, 0, 1, 1, 0]
    >>> # detect both edges
    >>> detectPeaks(x, edge='both', show=True)

    >>> x = [-2, 1, -2, 2, 1, 1, 3, 0]
    >>> # set threshold = 2
    >>> detectPeaks(x, threshold = 2, show=True)
    """

    x = np.atleast_1d(x).astype("float64")
    if x.size < 3:
        return np.array([], dtype=int)
    if valley:
        x = -x
    # find indices of all peaks
    dx = x[1:] - x[:-1]
    # handle NaN's
    indnan = np.where(np.isnan(x))[0]
    if indnan.size:
        x[indnan] = np.inf
        dx[np.where(np.isnan(dx))[0]] = np.inf
    ine, ire, ife = np.array([[], [], []], dtype=int)
    if not edge:
        ine = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) > 0))[0]
    else:
        if edge.lower() in ["rising", "both"]:
            ire = np.where((np.hstack((dx, 0)) <= 0) & (np.hstack((0, dx)) > 0))[0]
        if edge.lower() in ["falling", "both"]:
            ife = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) >= 0))[0]
    ind = np.unique(np.hstack((ine, ire, ife)))
    # handle NaN's
    if ind.size and indnan.size:
        # NaN's and values close to NaN's cannot be peaks
        ind = ind[
            np.in1d(
                ind, np.unique(np.hstack((indnan, indnan - 1, indnan + 1))), invert=True
            )
        ]
    # first and last values of x cannot be peaks
    if ind.size and ind[0] == 0:
        ind = ind[1:]
    if ind.size and ind[-1] == x.size - 1:
        ind = ind[:-1]
    # remove peaks < minimum peak height
    if ind.size and mph is not None:
        ind = ind[x[ind] >= mph]
    # remove peaks - neighbors < threshold
    if ind.size and threshold > 0:
        dx = np.min(np.vstack([x[ind] - x[ind - 1], x[ind] - x[ind + 1]]), axis=0)
        ind = np.delete(ind, np.where(dx < threshold)[0])
    # detect small peaks closer than minimum peak distance
    if ind.size and mpd > 1:
        ind = ind[np.argsort(x[ind])][::-1]  # sort ind by peak height
        idel = np.zeros(ind.size, dtype=bool)
        for i in range(ind.size):
            if not idel[i]:
                # keep peaks with the same height if kpsh is True
                idel = idel | (ind >= ind[i] - mpd) & (ind <= ind[i] + mpd) & (
                    x[ind[i]] > x[ind] if kpsh else True
                )
                idel[i] = 0  # Keep current peak
        # remove the small peaks and sort back the indices by their occurrence
        ind = np.sort(ind[~idel])

    if show:
        if indnan.size:
            x[indnan] = np.nan
        if valley:
            x = -x
        _plot(x, mph, mpd, threshold, edge, valley, ax, ind)

    return ind
