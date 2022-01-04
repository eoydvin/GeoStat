    # -*- coding: utf-8 -*-


import numpy as np
import matplotlib.pyplot as plt
import tqdm
import pandas as pd
from scipy.optimize import curve_fit


class OrdinaryKriging(object):
    """
    Init: Fits a semivariogram to given data
    Predict: Computes the ordinary Kriging equation given semivariogram
    
    """
    def __init__(self, xdata, ydata, zdata, variogram_parameters, 
                 enable_plotting, n_bins):
        """
        Parameters
        ----------
        xdata : numpy array
            x-koordinates of observations 
        ydata : numpy array
            y-coordinates of observations
        zdata : numpy array
            z-data of observations, in our case this is rain
        variogram_parameters : list
            [alpha, beta, hr, c0]
            alpha is usually: -3
            beta is 1 for exponential and 2 for gaussian variogram
            hr must be set (range)
            C0 must be set (nugget)
        enable_plotting : Bool
            Set to true if you want to plot best fit variogram
        nbins : int
            Number of averaging bins
    
        Returns None 
        Initialized Kriging object with fitted empirical variogram. 
        """
        self.xdata = xdata
        self.ydata = ydata
        self.zdata = zdata
        
        self.a = variogram_parameters[0]
        self.b = variogram_parameters[1]
        self.hr = variogram_parameters[2]
        self.C0 = variogram_parameters[3]  
        
        #for calculating cross terms
        x = np.array([xdata for i in range(len(xdata))]) 
        y = np.array([ydata for i in range(len(xdata))])
        z = np.array([zdata for i in range(len(xdata))])
        
        #calculate delta z
        self.gamma_matrix =  0.5*(z - z.T)**2 
        delta_z = self.gamma_matrix[np.triu_indices( # for semivariogram
            self.gamma_matrix.shape[0], k = 1)]
        
        #calculate distances
        self.h_matrix = np.sqrt((x - x.T)**2 + (y - y.T)**2) 
        h = self.h_matrix[np.triu_indices(self.h_matrix.shape[0], k = 1)] 
        
        #remove values outside range 
        df = pd.DataFrame({'h[m]':h, 'delta_p':delta_z})
        df_short = df[~(df['h[m]'] >= self.hr)]  # remove values outside range
        
        #divide into averaging bins
        bins = np.linspace(
            df_short['h[m]'].min(), df_short['h[m]'].max(), n_bins)
        bins_mid = (bins[1:] + bins[:-1]) / 2 #calculate midpoint of each bin
        
        #calcualte mean gamma in each bin
        h_n = 0 
        gamma_mean = []
        for h_n1 in bins_mid: 
            gamma_mean.append(df_short[(df_short['h[m]'].between(
                h_n, h_n1))]['delta_p'].mean())
            h_n = h_n1
        
        df_bins = pd.DataFrame([bins_mid, gamma_mean]).transpose()
        df_bins.dropna(subset = [1], inplace=True) #drop bins without data

        # fit curve to gamma values and distances
        C1, cov = curve_fit(f=self.gamma_h, xdata=df_bins[0], ydata=df_bins[1])        
        
        self.C1 = C1 # store for use in predict
        
        if enable_plotting is True:
            plt.plot(df_bins[0], df_bins[1], 'ob')
            plt.plot(np.linspace(0, max(df_short['h[m]'])), self.gamma_h(
                np.linspace(0, max(df_short['h[m]'])), self.C1), '-b')
            plt.plot(np.linspace(0, max(df_short['h[m]'])), self.cov_z(
                np.linspace(0, max(df_short['h[m]']))), '-g')
            plt.xlim(0, max(df_short['h[m]']))
            plt.show()
 
    def cov_z(self, h):
        """
        Computes covariance for given h. In this calss gamma_h is used to 
        find paramter C1. Then cov_z can be calculated by using the following 
        relation: 
            
            cov_z = C0 + C1 - gamma_h
            cov_z = C1*expt(alpha * ( (h / h_r)**beta))
        
        Parameters:
        ----------
        self.a : alpha parameter, user input. 
        self.hr : range of semivariogram, user input
        self.b : beta, user input
        self.C0 : Nugget value, user input.
        self.C1 : C0 + C1 is called the sill, Found by curve fitting in init.         

        """
        return self.C1*np.exp(self.a*(h/self.hr)**self.b)    
    
    def gamma_h(self, h, C1):
        """
        Computes gamma for given h. C1 is a variable found using curv fitting 
        in __init__. In the rest of the calculations C1 is a constant. 
        
        Parameters:
        ----------
        self.a : alpha parameter, user input. 
        self.hr : range of semivariogram, user input
        self.b : beta, user input
        self.C0 : Nugget value, user input.
        self.C1 : C0 + C1 is called the sill, found by curve fitting in init. 

        """
        return self.C0 + C1*(1 - np.exp(self.a*(h/float(self.hr))**self.b))   

    def predict(self, xgrid, ygrid):
        """
        Predicts interpolated values for a grid using Ordinary Kriging and the 
        variogram found in __init__. 
        
        Parameters:
        ----------
        xgrid: xgrid for estimation
        ygrid: ygrid for estimation
        
        Returns:
        z_grid_intp : interpolated values   
        
        """
                        
        #design_matrix = self.gamma_h(self.h_matrix, self.C1)            
        design_matrix = self.cov_z(self.h_matrix)
        
        design_matrix = np.append(design_matrix, np.ones([
            design_matrix.shape[1], 1]), axis=1) # extra column with ones
        design_matrix = np.append( #extra row with ones
            design_matrix, np.ones([1, design_matrix.shape[1]]), axis =0)
        design_matrix[-1, -1] = 0 #last element is zero
        
        
        design_matrix_inv = np.linalg.pinv(design_matrix) 
        z_grid_intp = np.zeros([ygrid.size, xgrid.size])
        z_grid_sigma = np.zeros([ygrid.size, xgrid.size])

        x_data_t = self.xdata.reshape(-1, 1) #matrix friendly
        y_data_t = self.ydata.reshape(-1, 1)
        z_data_t = self.zdata.reshape(-1, 1)
        
        #flip y so that we start upper left 
        #ygrid = np.flip(ygrid)
        
        for i in range(len(xgrid)):
            for j in range(len(ygrid)):
                # Distance from new point to measured points
                h = np.sqrt((x_data_t - xgrid[i])**2 + (y_data_t - ygrid[j])**2) 
                
                # Estimate gamma and cov for these distances
                cov_eo = self.cov_z(h) 
                
                # Append 1 to end of array
                cov_eo = np.append(cov_eo, np.array([[1]]), axis=0) 
                
                # Compute weigths
                w = design_matrix_inv @ cov_eo
                
                # Estimate z in point i, j
                z_grid_intp[j, i] = z_data_t.T @ w[0:-1] # remove mu_L from w
                z_grid_sigma[j, i] = self.cov_z(0) - w.T @ cov_eo
                
        return z_grid_intp, np.sqrt(z_grid_sigma)
