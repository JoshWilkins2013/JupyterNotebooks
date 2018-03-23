def interpolate(freq, power):
    ### Use to interpolate data such as OCXO phase noise at given offset frequencies
    ### Consider adding scale factor or numPoints to control interpolation

    import numpy as np

    freq = np.array(freq)
    power = np.array(power) - 100 # Ensure all values are negative
    logPower = np.log10([-x for x in power])

    newFreq = np.logspace(np.log10(min(freq)), np.log10(max(freq)), (len(freq)-1)*100)
    newPower = -10**(np.interp(np.log10(newFreq), np.log10(freq), logPower))
    return newFreq, newPower+100
