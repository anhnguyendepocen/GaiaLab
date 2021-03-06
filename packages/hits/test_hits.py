"""
Test suite for the hits module.


Toby James 2018
"""
import unittest
import numpy as np
import pandas as pd
import warnings
from numba import NumbaWarning
import math

#functions to run tests on
#equivalent to from . import * but more verbose
try:
    from hits.hitdetector import identify_anomaly, identify_noise, plot_anomaly
    from hits.hitsimulator import hit_distribution, flux, p_distribution, \
                                  freq, generate_event, generate_data, masses
    from hits.response.anomaly import isolate_anomaly, spline_anomaly
    from hits.response.characteristics import get_turning_points, \
                                              filter_turning_points
except(ImportError):
    from .hitdetector import identify_anomaly, identify_noise, plot_anomaly
    from .hitsimulator import hit_distribution, flux, p_distribution, freq, \
                              generate_event, generate_data, masses
    from .response.anomaly import isolate_anomaly, spline_anomaly
    from .response.characteristics import get_turning_points, \
                                          filter_turning_points


#------------hitdetector.py tests----------------------------------------------
class TestHitDetectorIdentifyFuncs(unittest.TestCase):

    def setUp(self):
        # Create dummy data with anomalies to test for hits.
        obmt = np.linspace(0,100,1000)
        rate = np.zeros(1000)
        # Generate a random number of hits between 1 and 20.
        self.hits = np.random.randint(1,20)
        
        hit_loc = np.linspace(0,999, self.hits)
        for i in hit_loc:
            rate[int(i)] = 4

        w1_rate = np.zeros(1000) # Value here is okay to be 0.
        
        self.df = pd.DataFrame(data=dict(obmt = obmt,
                                    rate = rate,
                                    w1_rate = w1_rate))

    def test_identify_anomaly_correctly_identifies(self):
        # Should identify 3 anomalies in the generated data.
        warnings.simplefilter("ignore", NumbaWarning)
        self.assertTrue(len(identify_anomaly(self.df)[1]) == self.hits)

    def test_identify_anomaly_return_shape(self):
        # Tests the function returns the expected dataframe shape.
        warnings.simplefilter("ignore", NumbaWarning)
        
        self.assertTrue(['obmt', 'rate', 'w1_rate', 'anomaly'] in \
        identify_anomaly(self.df)[0].columns.values)


#------------hitsimulator.py tests---------------------------------------------
class TestHitSimulatorNumericalFuncs(unittest.TestCase):
    
    def test_flux_expected_values_mass(self):
    # Test the flux function returns expected values.
        self.assertAlmostEqual(flux(2.7e-11), 5.388e-6, places=4, 
                               msg="Flux of particles of mass 2.7e-11 " \
                               "%r. Expected %r." % \
                               (flux(2.7e-11), 5.388e-6))

        self.assertAlmostEqual(flux(2.9e-11), 5.114e-6, places=4, 
                               msg="Flux of particles of mass 2.9e-11 " \
                               "returned %r. Expected %r." % \
                               (flux(2.9e-11), 5.114e-6))

    def test_freq_independent_of_mass_array(self):
    # The total frequency of a range should be the same irrespective of 
    # the array of masses passed.
        masses2 = np.linspace(1e-13, 1e-7, 100) 
        masses1_freq = sum(freq(masses))
        masses2_freq = sum(freq(masses2))
        self.assertAlmostEqual(masses1_freq, masses2_freq, places=4, 
                               msg="Total frequency of 100 mass array " \
                               "calculated as %r. Total frequency of " \
                               "10000 mass array calculated as %r." % \
                               (masses2_freq, masses1_freq))

class TestHitSimulatorGeneratorFuncs(unittest.TestCase):
    
    def test_expected_rate_of_impacts(self):
    # Test that generate_event creates expected rate of impact.
    # Conservative estimate used, expected rate is around 1% so it is 
    # run 100 times and tested that the total amount is no greater than 
    # 8. (Probability(X > 8 = 1e-6.)

    # Since this test is probabalistic it is difficult to test for 
    # certain. It is therefore at the user's discretion (and statistical
    # understanding) to decide at what point a failure truly indicates 
    # failure. 
        frequencies = freq(masses)
        count = 0
        for _ in range(1000):
            # int(bool( to turn any non zero number into 1.
            count += 1*int(bool(generate_event(masses, frequencies)[0])) 
        try:
            self.assertGreater(80, count)
        except(AssertionError):
            # Poisson distribution with rate parameter 1 - not exact 
            # but indicative.
            poisson_1000 = lambda x: (np.e**(-10))/math.factorial(x)
            # Probability of receiving a value of count or higher.
            probability = 1 - sum([poisson_100(x) for x in range(count)])

            raise RuntimeError("\n\n***\nUnexpectedly high hitrate produced " \
                               "by generate_data. Consider re-running tests." \
                               "\n1000 attempts yielded %r hits. The " \
                               "probability of this occurring is less than " \
                               "%.2e.\nIf this happens multiple times, use " \
                               "your statistical discretion to consider this "\
                               "a failure.\n***\n\n" % (count, probability))
            

#------------response.py tests-------------------------------------------------
class TestResponseTurningPointFuncs(unittest.TestCase):

    def setUp(self):
    # Set up dummy polynomial data with known number of turning points.
        obmt = np.linspace(0,100,1000)
        # Random number of turning points between 0 and 20.
        self.points = np.random.randint(1,20) 

        # Set up rate as a sin function over obmt with the expected 
        # number of turning points.
        rate = np.sin(self.points*np.pi*obmt/100) 
        w1_rate = np.zeros(1000)
        self.df = pd.DataFrame(data=dict(obmt = obmt,
                                         rate = rate,
                                         w1_rate = w1_rate))

    def test_get_turning_points(self):
        self.assertEqual(len(get_turning_points(self.df)),self.points)


    def test_filter_turning_points(self):
        self.assertTrue(len(filter_turning_points(self.df)) <= \
                        len(get_turning_points(self.df)))

#-------------------------------------------

if __name__ == "__main__":
    unittest.main()
