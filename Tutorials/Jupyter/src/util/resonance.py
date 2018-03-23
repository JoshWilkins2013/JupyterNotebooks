'''
resonance.py
Created on July 11, 2017
Adapted from zeeman.py in Mac-D Project

Class Definitions for Atomic Resonance Swept Data processing

@author: Dan.Boschen
'''
import numpy as np


class Sweep(object):
    '''
    Sweep Data, 2d array for multiple sweeps
    Object expects a 2D array consisting of multiple runs of measured
    resonance amplitude versus frequency offset
    '''

    def __init__(self, faxis, data):
        '''
        Constructor
        data: 2d array for multiple sweeps
        faxis: frequency axis in Hz
        '''
        self.data = data
        self.npts = np.shape(data)[0]
        self.faxis = faxis
        self.step = faxis[1]-faxis[0]

    def MeanFit(self):
        '''
        mean of data
        '''
        if (np.ndim(self.data) > 1):
            meanData = np.mean(self.data, axis=1)
        else:
            meanData = self.data
        return meanData

    def RabiFit(self):
        '''
        Rabi fit to mean value of data using Least Squares gradient method
        see https://docs.scipy.org/doc/scipy/
        reference/generated/scipy.optimize.least_squares.html
        '''
        from scipy.optimize import curve_fit


        meanRabi = self.MeanFit()
        
        # determine seed values
        center = np.argmax(meanRabi)
        fOffset = self.faxis[center]
        mid = (np.max(meanRabi) + np.min(meanRabi)) / 2
        indicesAboveMid = np.count_nonzero(meanRabi > mid)
        gammaEst = np.float(indicesAboveMid) * self.step
        # the following returns the first and last element
        # if less than 1 gamma from center
        start = np.where(center - indicesAboveMid > 0, center - indicesAboveMid, 0)
        stop = np.where(center + indicesAboveMid > self.npts, center + indicesAboveMid, self.npts)
        floorEst = np.mean(np.delete(meanRabi, range(start + 1, stop - 1)))
        ampEst = np.max(meanRabi) - floorEst

        A = 1
        T = 0.8/gammaEst

        bounds = ([A * .75, T*.1, ampEst*.1, floorEst*.1, fOffset-1/(2*T)],
                  [A * 1.25, T*10, ampEst*10, floorEst*10, fOffset+1/(2*T)])

        popt, pcov = curve_fit(self.__Rabi, self.faxis, meanRabi, bounds=bounds)
   
        self.param = {
                'A': popt[0],
                'T': popt[1],
                'C': popt[2],
                'floor': popt[3],
                'fOffset': popt[4]
        }
        
        stdErr = np.sqrt(np.diag(pcov))
        stdErrOut = {
                'Aerr': stdErr[0],
                'Terr': stdErr[1],
                'Cerr': stdErr[2],
                'floorErr': stdErr[3],
                'fOffsetErr': stdErr[4]
                }
        
        return self.param, stdErrOut


    def LorentzFit(self, errLim=1e-12, debug=False):
        '''
        UPDATE THIS TO PROCESS SAME AS RABIFIT
        
        Lorentzian fit to mean value of data using Least Squares gradient
        method

        see https://docs.scipy.org/doc/scipy/
        reference/generated/scipy.optimize.least_squares.html

        '''
        from scipy.optimize import least_squares

        # error function
        def __Err(params, freq, y):
            target = self.Lorentz(params, freq)
            if np.ndim(y) > 1:
                return target[:, np.newaxis] - y
            else:
                return target - y

        # Jacobian for Lorentzian funciton
        def __Jac(params, freq, y):
            # note least squares requires this to have 3 parameters
            gamma = params[0]
            amp = params[1]
            freqOff = params[2]
            den = (freq - freqOff) ** 2 + (gamma / 2) ** 2
            J = np.empty((freq.size, params.size))
            # partial derivative with respect to gamma:
            J[:, 0] = 8 * gamma * amp * (freq - freqOff) / (((gamma) ** 2 + 4 * (freq - freqOff)) ** 2)
            # partial derivative with respect to amp:
            J[:, 1] = (gamma / 2) ** 2 / den
            # partial derivative with respect to freqOff:
            J[:, 2] = 2 * (gamma / 2) ** 2 * (freq - freqOff) / den ** 2
            # partial derivative with respect floor:
            J[:, 3] = 1
            return J

        zeeman = self.MeanFit()

        # determine seed values
        # =====================================================
        mid = (np.max(zeeman) + np.min(zeeman)) / 2
        indicesAboveMid = np.count_nonzero(zeeman > mid)
        gammaEst = np.float(indicesAboveMid) * self.step
        center = np.argmax(zeeman)
        fOffset = self.faxis[center]
        # the following returns the first and last element if
        # less than 1 gamma from center
        start = np.where(center - indicesAboveMid > 0, center - indicesAboveMid, 0)
        stop = np.where(center + indicesAboveMid > self.npts, center + indicesAboveMid, self.npts)

        floorEst = np.mean(np.delete(zeeman, range(start + 1, stop - 1)))
        ampEst = np.max(zeeman) - floorEst
        # =====================================================

        params = [gammaEst, ampEst, fOffset, floorEst]
        # print(params)
        bounds = [(gammaEst * .75,
                   ampEst * .75,
                   - gammaEst,
                   floorEst * .9),
                  (gammaEst * 1.25,
                   ampEst * 1.25,
                   gammaEst, floorEst * 1.25)]

        if (debug):
            verbose = 2
        else:
            verbose = 1

        res = least_squares(__Err, params, jac=__Jac,
                            bounds=bounds, args=(self.faxis, zeeman),
                            ftol=errLim, xtol=errLim, gtol=errLim,
                            verbose=verbose)

        # over-ride amplitude to be actual peak
        # The overall mse is lower without this override, but
        res.x[1] = np.max(zeeman) - res.x[3]

        self.param = {
                'gamma': res.x[0],
                'amp': res.x[1],
                'foffset': res.x[2],
                'floor': res.x[3]
        }
        return self.param

    def displayParam(self):
        text = ""
        for key, item in self.param.iteritems():
            text += key + " = " + str(item) + "\n"
        return text

    def Lorentz(self, params, freq):
        gamma = params[0]
        amp = params[1]
        freqOff = params[2]
        floor = params[3]
        return (gamma ** 2 * amp / 4) * (1 / ((freq - freqOff) ** 2 + (gamma / 2) ** 2)) + floor

    def Rabi(self, freq, param=None):
        if not param:
            param = self.param
        A = param['A']
        T = param['T']
        C = param['C']
        floor = param['floor']
        fOffset = param['fOffset']
        return self.__Rabi(freq, A, T, C, floor, fOffset)

    def __Rabi(self, freq, A, T, C, floor, fOffset):
        # parametized Rabi function
        m = T / (np.pi)
        F = m / 2 * np.sqrt((A / m)**2 + (2 * np.pi * (freq - fOffset))**2)
        return C * (A * np.pi / 2 * np.sinc(F))**2 + floor

    def dRabi(self, freq, param=None):
        if not param:
            param = self.param
        A = param['A']
        T = param['T']
        C = param['C']
        floor = param['floor']
        fOffset = param['fOffset']
        return self.__dRabi(freq, A, T, C, floor, fOffset)

    def __dRabi(self, freq, A, T, C, floor, fOffset):
        # derivative of Rabi funciton
        m = T / (np.pi)
        F = m / 2 * np.sqrt((A / m)**2 + (2 * np.pi * (freq - fOffset))**2)
        first = (C * T**2) / 2 * (freq - fOffset) * (A * np.pi / F)**2
        second = (np.cos(np.pi * F) * np.sinc(F) - (np.sinc(F))**2)
        return first * second
