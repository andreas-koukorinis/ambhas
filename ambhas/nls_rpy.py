#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 23 17:58:52 2014

@author: Sat Kumar Tomer
@email: satkumartomer@gmail.com
@website: www.ambhas.com
"""

from __future__ import division

import numpy as np
from scipy.stats.distributions import  t

from rpy2.robjects import r
import rpy2.robjects.numpy2ri
rpy2.robjects.numpy2ri.activate()
r('library(alr3)')


class Nls():
    """
    This class performs the non linear regression using R library
        
    Example:
        
    """
    
    def __init__(self, x, y, p=3, eq='a*x^b+c', par_ini = 'a=3,b=0.3,c=-15'):
        """ initialise the class with X and Y
        Input:
            x:        one dimensional numpy array
            y:        one dimensional numpy array
            p:  number of parameters
            eq:   equation to be fitted
            par_init: string containing the initial estimates of the parameters
            
            Note: the size of x and y should be same
        """
        self.x = x
        self.y = y
        self.eq = eq
        self.par_ini = par_ini
        self.n = len(x)
        self.p = p
    
    def fit(self, summary=False, lower=None, upper =None):
        self.lower = lower
        self.upper = upper
        x = self.x
        y = self.y
        eq = self.eq
        par_ini = self.par_ini
        
        r.assign('x',x)
        r.assign('y',y)
        r('control.foo <- nls.control(maxiter=100, minFactor = 1/4096)')
        
        if lower is not None and upper is not None:
            r('fit <- nls(y ~ %s, start = list(%s), control=control.foo, algorithm = "port", lower=list(%s), upper=list(%s))'%(eq,par_ini,lower,upper))
        else:
            r('fit <- nls(y ~ %s, start = list(%s), control=control.foo)'%(eq,par_ini))
        r('summary_fit <- summary(fit)')
        par = np.array(r('coef(summary_fit)'))
        
        if summary:
            print r('summary(fit)')
            print r('coef(fit)')
            print r('summary(fit)$cov.unscaled * summary(fit)$sigma^2')
            
        return par    
    
    def predict(self,x_eval,alpha=0.05):
        """
        0.05 means 95 % confidence interval
        """
        self.fit(lower=self.lower, upper=self.upper)
        n = self.n
        p = self.p
        print r('fit')
        dof = n-p
        tval = t.ppf(1-alpha/2., dof) 
                
        y_hat = np.empty(x_eval.shape)
        y_hat_se = np.empty(x_eval.shape)
        for i in xrange(len(x_eval)):
            li = self.eq.rsplit('x', 1)
            eq_x = ('%f'%x_eval[i]).join(li)
            #eq_x = self.eq.replace('x','%f'%x_eval[i])
                        
            #foo = np.array(r('delta.method(fit, "%s")'%eq_x))
            foo = np.array(r('deltaMethod(fit, "%s")'%eq_x))
            y_hat[i] = foo[0]
            y_hat_se[i] = foo[1]
        y_ul = y_hat + tval*y_hat_se
        y_ll = y_hat - tval*y_hat_se
                
        return y_hat, y_ul, y_ll
    
    
    
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    a = 10
    b = 0.5
    c = -15
    #x = np.random.rand(25,)
    #y = a*x**b +c + 0.1*np.random.normal(size=25,)
    #foo = Nls(x,y)
    foo = Nls(x, y, p=4, eq='a + (b-a)/(1+exp(-k*(x-c)))', par_ini = 'a=0,b=8,c=4.1,k=5.0')
    par = foo.fit(lower='0,0,0,0', upper='2,10,10,10')
    
    #print par[:,0]
    x_eval = np.linspace(3,7)
    y_hat, y_ul, y_ll = foo.predict(x_eval, alpha=0.05)
    
    plt.plot(x,y,'.')
    plt.plot(x_eval, y_hat)
    plt.plot(x_eval, y_ul, '--')
    plt.plot(x_eval, y_ll, '--')
    plt.show()
    
    
