#!/home/markos/anaconda3/bin/python

from robot import Robot
import numpy as np
from pdb import set_trace

class PathPlanning():

    def __init__(self, R, T=0.01):
        self.R = R
        self.integrator_ = self.R.state  # initial state of Robot
        self.differentiator_ = np.array([ self.R.fk()[0,3], self.R.fk()[1,3] ])  # initial position of tool
        self.Logic_ = 'MinEnergy'
        self.T = T

    def reset(self):
        """
        Reset system: reset integrator, differentiator, and Robot
        to HOME position
        """

        self.R.reset()
        self.integrator_ = self.R.state
        self.differentiator_ = np.array([ self.R.fk()[0,3], self.R.fk()[1,3] ])  # initial position of tool

    def differentiator(self,input):
        ret = (input - self.differentiator_)/self.T
        self.differentiator_ = input
        return ret

    def logic(self,input):
        """
        Path planning Logic <3
        This is the heart of the robot
        here we decide depending on the spcecified task
        the desired joint velocities
        """

        if self.Logic_ == 'MinEnergy':  # one Task only (for testing)
            Jplus = np.linalg.pinv(self.R.Jacobian()) 
            # caluclate q dots
            out = Jplus[:,:2] @ input  # FIX: zeropad input to 6 dimentions
        return out
    
    def integrator(self,input):
        self.integrator_ = input*self.T + self.integrator_
        return self.integrator_

    def trajectoryPlan(self,Pa,Pb,tf):
        """
        Calculate a streight line path from Pa to Pb
        according to a 2nd degree velocity profile
        v(t) = a*t^2 + b*t + c
        p(t) = integral_of v(t)
        returns: velocity_profile, position_profile, time(sec) (arrays)
        """
 
        time = np.linspace(0, tf, tf/self.T)
        # calculate polynomials
        a = 6*(Pa-Pb)/tf**3
        b = -a*tf
        c = 0
        d = Pa
        p = np.zeros((2,time.shape[0]))
        v = np.zeros((2,time.shape[0]))
        for i,t in enumerate(time): # FIX: create vectorized function
            p[:,i] = (a*t**3)/3 + (b*t**2)/2 + d
            v[:,i] = a*t**2 + b*t
        return v, p, time

    def move(self,Pb,tf):
        """
        """
        Pa = np.array([ self.R.fk()[0,3], self.R.fk()[1,3] ])  # initial position of tool
        move_states = []
        v, p, time = self.trajectoryPlan(Pa,Pb,tf)
        for i in range(time.shape[0]):
            q = self.integrator(self.logic(self.differentiator(p[:,i])))
            self.R.move(q)
            move_states.append(q) 
        return move_states
            
