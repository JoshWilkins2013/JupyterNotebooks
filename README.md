# Jupyter Notebooks

Collection of miscellaneous analyses done in jupyter.<br>
See here for the binder (A jupyter server hosting these files!):<br>
https://hub.mybinder.org/user/joshwilkins2013-jupyternotebooks-fkoz5x28/tree

## Output Power Controller

An adjustable output power stabilizer circuit utilized in a 12 GHz synthesizer. 
Designed with both the ADL6010 and the LTC5564 envelope detectors.

## Quantization Error

Sampling a signal causes rounding errors, produced by the difference in the actual value 
of the signal to the measurable value. This notebook takes a look at preconditioning 
the signal to reduce this error.

## Stepped Input Response

Given a stepped input, the output at the 'hold' regions (transient responses) are captured. 
The script returns two csv files; The averaged results and the transient responses.