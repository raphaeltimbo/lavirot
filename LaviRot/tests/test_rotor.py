import os
import pytest
from LaviRot.elements import *
from LaviRot.rotor import *
from LaviRot.rotor import MAC_modes
from LaviRot.materials import steel
import numpy as np
from numpy.testing import assert_almost_equal, assert_allclose

test_dir = os.path.dirname(__file__)


@pytest.fixture
def rotor1():
    #  Rotor without damping with 2 shaft elements - no disks and no bearings
    le_ = 0.25
    i_d_ = 0
    o_d_ = 0.05

    tim0 = ShaftElement(le_, i_d_, o_d_, steel,
                        shear_effects=True,
                        rotary_inertia=True,
                        gyroscopic=True)
    tim1 = ShaftElement(le_, i_d_, o_d_, steel,
                        shear_effects=True,
                        rotary_inertia=True,
                        gyroscopic=True)

    shaft_elm = [tim0, tim1]
    return Rotor(shaft_elm, [], [])


def test_rotor_attributes(rotor1):
    assert len(rotor1.nodes) == 3
    assert len(rotor1.nodes_i_d) == 3
    assert len(rotor1.nodes_o_d) == 3
    assert rotor1.L == 0.5
    assert rotor1.m_disks == 0
    assert rotor1.m_shaft == 7.6674495701675891
    assert rotor1.m == 7.6674495701675891
    assert rotor1.nodes_pos[0] == 0
    assert rotor1.nodes_pos[1] == 0.25
    assert rotor1.nodes_pos[-1] == 0.5


def test_index_eigenvalues_rotor1(rotor1):
    evalues = np.array([-3.8 + 68.6j, -3.8 - 68.6j, -1.8 + 30.j, -1.8 - 30.j, -0.7 + 14.4j, -0.7 - 14.4j])
    evalues2 = np.array([0. + 68.7j, 0. - 68.7j, 0. + 30.1j, 0. - 30.1j, -0. + 14.4j, -0. - 14.4j])
    assert_almost_equal([4, 2, 0, 1, 3, 5], rotor1._index(evalues))
    assert_almost_equal([4, 2, 0, 1, 3, 5], rotor1._index(evalues2))


def test_mass_matrix_rotor1(rotor1):
    Mr1 = np.array([[ 1.421,  0.   ,  0.   ,  0.049,  0.496,  0.   ,  0.   , -0.031,  0.   ,  0.   ,  0.   ,  0.   ],
                    [ 0.   ,  1.421, -0.049,  0.   ,  0.   ,  0.496,  0.031,  0.   ,  0.   ,  0.   ,  0.   ,  0.   ],
                    [ 0.   , -0.049,  0.002,  0.   ,  0.   , -0.031, -0.002,  0.   ,  0.   ,  0.   ,  0.   ,  0.   ],
                    [ 0.049,  0.   ,  0.   ,  0.002,  0.031,  0.   ,  0.   , -0.002,  0.   ,  0.   ,  0.   ,  0.   ],
                    [ 0.496,  0.   ,  0.   ,  0.031,  2.841,  0.   ,  0.   ,  0.   ,  0.496,  0.   ,  0.   , -0.031],
                    [ 0.   ,  0.496, -0.031,  0.   ,  0.   ,  2.841,  0.   ,  0.   ,  0.   ,  0.496,  0.031,  0.   ],
                    [ 0.   ,  0.031, -0.002,  0.   ,  0.   ,  0.   ,  0.005,  0.   ,  0.   , -0.031, -0.002,  0.   ],
                    [-0.031,  0.   ,  0.   , -0.002,  0.   ,  0.   ,  0.   ,  0.005,  0.031,  0.   ,  0.   , -0.002],
                    [ 0.   ,  0.   ,  0.   ,  0.   ,  0.496,  0.   ,  0.   ,  0.031,  1.421,  0.   ,  0.   , -0.049],
                    [ 0.   ,  0.   ,  0.   ,  0.   ,  0.   ,  0.496, -0.031,  0.   ,  0.   ,  1.421,  0.049,  0.   ],
                    [ 0.   ,  0.   ,  0.   ,  0.   ,  0.   ,  0.031, -0.002,  0.   ,  0.   ,  0.049,  0.002,  0.   ],
                    [ 0.   ,  0.   ,  0.   ,  0.   , -0.031,  0.   ,  0.   , -0.002, -0.049,  0.   ,  0.   ,  0.002]])

    assert_almost_equal(rotor1.M(), Mr1, decimal=3)


def test_raise_if_element_outside_shaft():
    le_ = 0.25
    i_d_ = 0
    o_d_ = 0.05

    tim0 = ShaftElement(le_, i_d_, o_d_, steel,
                        shear_effects=True,
                        rotary_inertia=True,
                        gyroscopic=True)
    tim1 = ShaftElement(le_, i_d_, o_d_, steel,
                        shear_effects=True,
                        rotary_inertia=True,
                        gyroscopic=True)

    shaft_elm = [tim0, tim1]
    disk0 = DiskElement(3, steel, 0.07, 0.05, 0.28)
    stf = 1e6
    bearing0 = BearingElement(0, kxx=stf, cxx=0)
    bearing1 = BearingElement(3, kxx=stf, cxx=0)
    bearings = [bearing0, bearing1]

    with pytest.raises(ValueError) as excinfo:
        Rotor(shaft_elm, [disk0])
    assert 'Trying to set disk or bearing outside shaft' == str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        Rotor(shaft_elm, bearing_seal_elements=bearings)
    assert 'Trying to set disk or bearing outside shaft' == str(excinfo.value)


@pytest.fixture
def rotor2():
    #  Rotor without damping with 2 shaft elements 1 disk and 2 bearings
    le_ = 0.25
    i_d_ = 0
    o_d_ = 0.05

    tim0 = ShaftElement(le_, i_d_, o_d_, steel,
                        shear_effects=True,
                        rotary_inertia=True,
                        gyroscopic=True)
    tim1 = ShaftElement(le_, i_d_, o_d_, steel,
                        shear_effects=True,
                        rotary_inertia=True,
                        gyroscopic=True)

    shaft_elm = [tim0, tim1]
    disk0 = DiskElement(1, steel, 0.07, 0.05, 0.28)
    stf = 1e6
    bearing0 = BearingElement(0, kxx=stf, cxx=0)
    bearing1 = BearingElement(2, kxx=stf, cxx=0)

    return Rotor(shaft_elm, [disk0], [bearing0, bearing1])


def test_mass_matrix_rotor2(rotor2):
    Mr2 = np.array([[  1.421,   0.   ,   0.   ,   0.049,   0.496,   0.   ,   0.   ,  -0.031,   0.   ,   0.   ,   0.   ,   0.   ],
                    [  0.   ,   1.421,  -0.049,   0.   ,   0.   ,   0.496,   0.031,   0.   ,   0.   ,   0.   ,   0.   ,   0.   ],
                    [  0.   ,  -0.049,   0.002,   0.   ,   0.   ,  -0.031,  -0.002,   0.   ,   0.   ,   0.   ,   0.   ,   0.   ],
                    [  0.049,   0.   ,   0.   ,   0.002,   0.031,   0.   ,   0.   ,  -0.002,   0.   ,   0.   ,   0.   ,   0.   ],
                    [  0.496,   0.   ,   0.   ,   0.031,  35.431,   0.   ,   0.   ,   0.   ,   0.496,   0.   ,   0.   ,  -0.031],
                    [  0.   ,   0.496,  -0.031,   0.   ,   0.   ,  35.431,   0.   ,   0.   ,   0.   ,   0.496,   0.031,   0.   ],
                    [  0.   ,   0.031,  -0.002,   0.   ,   0.   ,   0.   ,   0.183,   0.   ,   0.   ,  -0.031,  -0.002,   0.   ],
                    [ -0.031,   0.   ,   0.   ,  -0.002,   0.   ,   0.   ,   0.   ,   0.183,   0.031,   0.   ,   0.   ,  -0.002],
                    [  0.   ,   0.   ,   0.   ,   0.   ,   0.496,   0.   ,   0.   ,   0.031,   1.421,   0.   ,   0.   ,  -0.049],
                    [  0.   ,   0.   ,   0.   ,   0.   ,   0.   ,   0.496,  -0.031,   0.   ,   0.   ,   1.421,   0.049,   0.   ],
                    [  0.   ,   0.   ,   0.   ,   0.   ,   0.   ,   0.031,  -0.002,   0.   ,   0.   ,   0.049,   0.002,   0.   ],
                    [  0.   ,   0.   ,   0.   ,   0.   ,  -0.031,   0.   ,   0.   ,  -0.002,  -0.049,   0.   ,   0.   ,   0.002]])
    assert_almost_equal(rotor2.M(), Mr2, decimal=3)


def test_a0_0_matrix_rotor2(rotor2):
    A0_0 = np.array([[ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.]])
    assert_almost_equal(rotor2.A()[:12, :12], A0_0, decimal=3)


def test_a0_1_matrix_rotor2(rotor2):
    A0_1 = np.array([[ 1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  1.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  1.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  1.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  1.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  1.]])
    assert_almost_equal(rotor2.A()[:12, 12:24], A0_1, decimal=3)


def test_a1_0_matrix_rotor2(rotor2):
    A1_0 = np.array([[  20.63 ,   -0.   ,    0.   ,    4.114,  -20.958,    0.   ,    0.   ,    1.11 ,    0.056,   -0.   ,   -0.   ,   -0.014],
                     [   0.   ,   20.63 ,   -4.114,    0.   ,   -0.   ,  -20.958,   -1.11 ,    0.   ,   -0.   ,    0.056,    0.014,    0.   ],
                     [   0.   ,  697.351, -131.328,    0.   ,   -0.   , -705.253,  -44.535,    0.   ,   -0.   ,    2.079,    0.596,    0.   ],
                     [-697.351,    0.   ,   -0.   , -131.328,  705.253,   -0.   ,   -0.   ,  -44.535,   -2.079,    0.   ,    0.   ,    0.596],
                     [   0.442,    0.   ,   -0.   ,    0.072,   -0.887,   -0.   ,   -0.   ,   -0.   ,    0.442,    0.   ,    0.   ,   -0.072],
                     [   0.   ,    0.442,   -0.072,    0.   ,   -0.   ,   -0.887,    0.   ,    0.   ,    0.   ,    0.442,    0.072,   -0.   ],
                     [   0.   ,    6.457,   -0.837,    0.   ,   -0.   ,    0.   ,   -1.561,    0.   ,   -0.   ,   -6.457,   -0.837,   -0.   ],
                     [  -6.457,   -0.   ,    0.   ,   -0.837,    0.   ,    0.   ,    0.   ,   -1.561,    6.457,    0.   ,    0.   ,   -0.837],
                     [   0.056,   -0.   ,    0.   ,    0.014,  -20.958,    0.   ,    0.   ,   -1.11 ,   20.63 ,    0.   ,    0.   ,   -4.114],
                     [   0.   ,    0.056,   -0.014,    0.   ,   -0.   ,  -20.958,    1.11 ,    0.   ,    0.   ,   20.63 ,    4.114,   -0.   ],
                     [  -0.   ,   -2.079,    0.596,   -0.   ,    0.   ,  705.253,  -44.535,   -0.   ,   -0.   , -697.351, -131.328,    0.   ],
                     [   2.079,    0.   ,   -0.   ,    0.596, -705.253,   -0.   ,    0.   ,  -44.535,  697.351,    0.   ,    0.   , -131.328]])
    assert_almost_equal(rotor2.A()[12:24, :12]/1e7, A1_0, decimal=3)


def test_a1_1_matrix_rotor2(rotor2):
    A1_1 = np.array([[ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.]])
    assert_almost_equal(rotor2.A()[12:24, 12:24] / 1e7, A1_1, decimal=3)


def test_evals_sorted_rotor2(rotor2):
    evals_sorted = np.array([  1.4667459679e-12 +215.3707255735j,   3.9623200168e-12 +215.3707255733j,
                               7.4569772223e-11 +598.0247411492j,   1.1024641658e-11 +598.0247411456j,
                               4.3188161105e-09+3956.2249777612j,   2.5852376472e-11+3956.2249797838j,
                               4.3188161105e-09-3956.2249777612j,   2.5852376472e-11-3956.2249797838j,
                               7.4569772223e-11 -598.0247411492j,   1.1024641658e-11 -598.0247411456j,
                               1.4667459679e-12 -215.3707255735j,   3.9623200168e-12 -215.3707255733j])

    evals_sorted_w_10000 = np.array([ -4.838034e-14  +34.822138j,  -5.045245e-01 +215.369011j,
                                      5.045245e-01 +215.369011j,   8.482603e-08+3470.897616j,
                                      4.878990e-07+3850.212629j,   4.176291e+01+3990.22903j ,
                                      4.176291e+01-3990.22903j ,   4.878990e-07-3850.212629j,
                                      8.482603e-08-3470.897616j,   5.045245e-01 -215.369011j,
                                      -5.045245e-01 -215.369011j,  -4.838034e-14  -34.822138j])

    rotor2_evals, rotor2_evects = rotor2._eigen()
    assert_allclose(rotor2_evals, evals_sorted, rtol=1e-3)
    assert_allclose(rotor2.evalues, evals_sorted, rtol=1e-3)
    rotor2.w = 10000
    assert_allclose(rotor2.evalues, evals_sorted_w_10000, rtol=1e-1)


@pytest.fixture
def rotor3():
    #  Rotor without damping with 6 shaft elements 2 disks and 2 bearings
    i_d = 0
    o_d = 0.05
    n = 6
    L = [0.25 for _ in range(n)]

    shaft_elem = [ShaftElement(l, i_d, o_d, steel,
                               shear_effects=True,
                               rotary_inertia=True,
                               gyroscopic=True) for l in L]

    disk0 = DiskElement(2, steel, 0.07, 0.05, 0.28)
    disk1 = DiskElement(4, steel, 0.07, 0.05, 0.35)

    stfx = 1e6
    stfy = 0.8e6
    bearing0 = BearingElement(0, kxx=stfx, kyy=stfy, cxx=0)
    bearing1 = BearingElement(6, kxx=stfx, kyy=stfy, cxx=0)

    return Rotor(shaft_elem, [disk0, disk1], [bearing0, bearing1])


def test_evects_sorted_rotor3(rotor3):
    evects_sorted = np.array([[ -4.056e-16 +8.044e-15j,   6.705e-19 -1.153e-03j,  -2.140e-15 +2.486e-14j,  -7.017e-17 +8.665e-04j],
                              [ -4.507e-17 -1.454e-03j,   5.888e-16 -1.658e-14j,  -1.698e-16 +9.784e-04j,   6.498e-16 +6.575e-14j],
                              [  3.930e-16 +4.707e-03j,  -1.916e-15 +5.753e-14j,   1.493e-17 +3.452e-04j,   2.575e-16 +1.289e-14j],
                              [ -1.988e-15 +3.816e-14j,  -5.225e-17 -4.648e-03j,  -1.167e-16 -3.922e-14j,   1.538e-16 -1.023e-04j],
                              [ -8.603e-16 +1.698e-14j,  -3.537e-17 -2.271e-03j,  -2.048e-15 +1.606e-14j,   1.939e-17 +8.099e-04j],
                              [ -1.022e-16 -2.586e-03j,   1.047e-15 -3.047e-14j,  -1.993e-16 +8.642e-04j,   5.357e-16 +6.104e-14j],
                              [  3.437e-16 +4.153e-03j,  -1.638e-15 +5.135e-14j,  -1.607e-17 +6.848e-04j,   4.770e-16 +3.704e-14j],
                              [ -1.736e-15 +3.413e-14j,  -1.168e-16 -4.098e-03j,   8.543e-16 -4.710e-14j,   1.840e-16 -4.807e-04j],
                              [ -1.298e-15 +2.574e-14j,  -7.387e-17 -3.118e-03j,  -1.588e-15 -7.947e-15j,   5.808e-17 +5.782e-04j],
                              [ -1.974e-16 -3.445e-03j,   1.381e-15 -4.169e-14j,  -1.433e-16 +5.933e-04j,   3.236e-16 +4.312e-14j],
                              [  2.387e-16 +2.529e-03j,  -1.028e-15 +3.221e-14j,  -2.678e-16 +1.561e-03j,   1.039e-15 +1.022e-13j],
                              [ -1.085e-15 +2.105e-14j,  -3.912e-17 -2.485e-03j,   3.717e-15 -4.134e-14j,   5.483e-17 -1.463e-03j],
                              [ -1.457e-15 +2.827e-14j,  -7.171e-17 -3.463e-03j,  -3.515e-16 -1.138e-14j,   3.815e-17 +1.101e-04j],
                              [ -2.795e-16 -3.800e-03j,   1.573e-15 -4.573e-14j,  -5.757e-17 +1.120e-04j,   3.794e-17 +1.081e-14j],
                              [  6.589e-18 +2.699e-04j,  -1.258e-16 +5.309e-15j,  -5.315e-16 +2.124e-03j,   1.364e-15 +1.555e-13j],
                              [ -2.067e-16 +3.324e-15j,  -3.704e-19 -2.394e-04j,   5.665e-15 -1.530e-14j,  -2.417e-16 -2.095e-03j],
                              [ -1.287e-15 +2.544e-14j,  -2.928e-17 -3.224e-03j,   1.039e-15 +1.573e-15j,  -3.299e-17 -3.849e-04j],
                              [ -1.851e-16 -3.567e-03j,   1.468e-15 -4.382e-14j,   1.043e-16 -3.941e-04j,  -2.973e-16 -2.819e-14j],
                              [ -1.492e-16 -2.150e-03j,   8.603e-16 -2.432e-14j,  -4.512e-16 +1.755e-03j,   1.236e-15 +1.412e-13j],
                              [  8.553e-16 -1.661e-14j,   1.701e-17 +2.167e-03j,   4.628e-15 +4.535e-14j,  -2.653e-16 -1.672e-03j],
                              [ -1.023e-15 +2.015e-14j,   3.903e-18 -2.426e-03j,   1.846e-15 +8.393e-15j,   6.506e-18 -6.765e-04j],
                              [ -9.796e-17 -2.771e-03j,   1.179e-15 -3.432e-14j,   1.394e-16 -7.208e-04j,  -5.197e-16 -5.518e-14j],
                              [ -2.651e-16 -4.008e-03j,   1.614e-15 -4.657e-14j,  -1.703e-16 +9.358e-04j,   5.812e-16 +8.236e-14j],
                              [  1.629e-15 -3.212e-14j,   1.655e-16 +4.011e-03j,   2.089e-15 +5.726e-14j,  -1.483e-16 -7.478e-04j],
                              [ -5.683e-16 +1.120e-14j,   1.973e-18 -1.316e-03j,   2.135e-15 +2.161e-14j,  -1.782e-16 -8.042e-04j],
                              [ -1.326e-16 -1.661e-03j,   6.747e-16 -2.122e-14j,   2.023e-16 -9.021e-04j,  -6.436e-16 -7.128e-14j],
                              [ -2.641e-16 -4.641e-03j,   1.899e-15 -5.464e-14j,  -8.833e-17 +6.219e-04j,   3.673e-16 +5.731e-14j],
                              [  1.912e-15 -3.674e-14j,   8.212e-17 +4.639e-03j,   1.118e-15 +5.106e-14j,  -1.381e-16 -3.957e-04j],
                              [ -6.649e-13 -3.259e-14j,   9.993e-02 +1.484e-16j,  -6.328e-12 -5.265e-13j,  -2.377e-01 -2.190e-14j],
                              [  1.202e-01 +3.939e-15j,   1.437e-12 +4.632e-14j,  -2.490e-01 +1.433e-14j,  -1.804e-11 +1.579e-13j],
                              [ -3.890e-01 -1.104e-16j,  -4.986e-12 -1.506e-13j,  -8.786e-02 +2.066e-14j,  -3.536e-12 +4.313e-14j],
                              [ -3.154e-12 -1.584e-13j,   4.028e-01 -4.557e-16j,   9.983e-12 -3.182e-14j,   2.806e-02 +5.927e-14j],
                              [ -1.403e-12 -7.024e-14j,   1.968e-01 -9.752e-16j,  -4.087e-12 -5.170e-13j,  -2.222e-01 -8.547e-15j],
                              [  2.138e-01 -3.508e-16j,   2.641e-12 +8.131e-14j,  -2.199e-01 +3.955e-15j,  -1.674e-11 +1.529e-13j],
                              [ -3.432e-01 +1.993e-15j,  -4.450e-12 -1.318e-13j,  -1.743e-01 +2.838e-14j,  -1.016e-11 +9.643e-14j],
                              [ -2.821e-12 -1.418e-13j,   3.552e-01 +1.011e-15j,   1.199e-11 +2.189e-13j,   1.319e-01 +5.933e-14j],
                              [ -2.127e-12 -1.070e-13j,   2.702e-01 -1.220e-15j,   2.023e-12 -4.081e-13j,  -1.586e-01 +2.107e-14j],
                              [  2.847e-01 +5.856e-16j,   3.613e-12 +1.088e-13j,  -1.510e-01 -5.642e-15j,  -1.183e-11 +1.084e-13j],
                              [ -2.090e-01 -6.114e-16j,  -2.791e-12 -8.398e-14j,  -3.973e-01 -4.666e-15j,  -2.804e-11 +2.739e-13j],
                              [ -1.740e-12 -9.060e-14j,   2.154e-01 +2.735e-15j,   1.052e-11 +9.056e-13j,   4.013e-01 +2.727e-14j],
                              [ -2.336e-12 -1.183e-13j,   3.001e-01 -1.686e-15j,   2.896e-12 -9.755e-14j,  -3.019e-02 +1.411e-14j],
                              [  3.141e-01 +3.027e-16j,   3.963e-12 +1.216e-13j,  -2.852e-02 -9.895e-15j,  -2.965e-12 +2.787e-14j],
                              [ -2.231e-02 -7.712e-16j,  -4.601e-13 -1.276e-14j,  -5.407e-01 -1.298e-14j,  -4.266e-11 +3.859e-13j],
                              [ -2.747e-13 -1.805e-14j,   2.074e-02 +1.739e-15j,   3.895e-12 +1.389e-12j,   5.747e-01 -1.335e-14j],
                              [ -2.103e-12 -1.056e-13j,   2.794e-01 +4.152e-15j,  -4.003e-13 +2.638e-13j,   1.056e-01 -1.101e-14j],
                              [  2.948e-01 +2.284e-15j,   3.797e-12 +1.154e-13j,   1.003e-01 +2.587e-15j,   7.733e-12 -7.168e-14j],
                              [  1.777e-01 -1.271e-15j,   2.108e-12 +6.492e-14j,  -4.467e-01 -1.871e-14j,  -3.874e-11 +3.205e-13j],
                              [  1.373e-12 +6.849e-14j,  -1.877e-01 +3.120e-15j,  -1.154e-11 +1.153e-12j,   4.588e-01 -3.120e-14j],
                              [ -1.665e-12 -8.544e-14j,   2.102e-01 +9.552e-16j,  -2.136e-12 +4.515e-13j,   1.856e-01 -4.985e-15j],
                              [  2.290e-01 -6.196e-16j,   2.974e-12 +8.935e-14j,   1.835e-01 -7.359e-15j,   1.514e-11 -1.221e-13j],
                              [  3.313e-01 +2.523e-16j,   4.036e-12 +1.236e-13j,  -2.382e-01 +6.579e-15j,  -2.259e-11 +1.654e-13j],
                              [  2.655e-12 +1.347e-13j,  -3.476e-01 +8.013e-16j,  -1.457e-11 +5.232e-13j,   2.051e-01 -1.595e-14j],
                              [ -9.256e-13 -4.619e-14j,   1.141e-01 +1.417e-15j,  -5.501e-12 +5.233e-13j,   2.206e-01 -2.267e-15j],
                              [  1.373e-01 -4.564e-15j,   1.838e-12 +5.302e-14j,   2.296e-01 -8.382e-15j,   1.955e-11 -1.490e-13j],
                              [  3.836e-01 +1.840e-16j,   4.735e-12 +1.445e-13j,  -1.583e-01 +9.794e-15j,  -1.572e-11 +1.066e-13j],
                              [  3.037e-12 +1.550e-13j,  -4.020e-01 +1.116e-15j,  -1.300e-11 +2.719e-13j,   1.086e-01 -6.340e-15j]])

    rotor3_evals, rotor3_evects = rotor3._eigen()
    mac1 = MAC_modes(evects_sorted, rotor3_evects[:, :4], plot=False)
    mac2 = MAC_modes(evects_sorted, rotor3.evectors[:, :4], plot=False)
    assert_allclose(mac1.diagonal(), np.ones_like(mac1.diagonal()))
    assert_allclose(mac2.diagonal(), np.ones_like(mac1.diagonal()))


@pytest.mark.skip(reason='Different evector order when not sorted')
def test_evects_not_sorted_rotor3(rotor3):
    evects = np.array([[ -1.153e-03 +2.437e-20j,  -1.153e-03 -2.437e-20j,  -2.681e-18 +6.093e-17j,  -2.681e-18 -6.093e-17j],
                       [  2.532e-16 -1.888e-19j,   2.532e-16 +1.888e-19j,   5.543e-18 -1.454e-03j,   5.543e-18 +1.454e-03j],
                       [ -8.195e-16 +6.110e-19j,  -8.195e-16 -6.110e-19j,   2.826e-17 +4.707e-03j,   2.826e-17 -4.707e-03j],
                       [ -4.648e-03 +9.316e-20j,  -4.648e-03 -9.316e-20j,   2.284e-18 +1.820e-16j,   2.284e-18 -1.820e-16j],
                       [ -2.271e-03 +6.619e-20j,  -2.271e-03 -6.619e-20j,   7.094e-18 +1.117e-16j,   7.094e-18 -1.117e-16j],
                       [  4.503e-16 -3.358e-19j,   4.503e-16 +3.358e-19j,   4.878e-18 -2.586e-03j,   4.878e-18 +2.586e-03j],
                       [ -7.230e-16 +5.391e-19j,  -7.230e-16 -5.391e-19j,   2.309e-17 +4.153e-03j,   2.309e-17 -4.153e-03j],
                       [ -4.098e-03 +9.646e-20j,  -4.098e-03 -9.646e-20j,   6.285e-18 +1.507e-16j,   6.285e-18 -1.507e-16j],
                       [ -3.118e-03 +7.505e-20j,  -3.118e-03 -7.505e-20j,   5.038e-18 +1.360e-16j,   5.038e-18 -1.360e-16j],
                       [  5.998e-16 -4.472e-19j,   5.998e-16 +4.472e-19j,  -5.367e-18 -3.445e-03j,  -5.367e-18 +3.445e-03j],
                       [ -4.403e-16 +3.283e-19j,  -4.403e-16 -3.283e-19j,   3.491e-17 +2.529e-03j,   3.491e-17 -2.529e-03j],
                       [ -2.485e-03 +6.818e-20j,  -2.485e-03 -6.818e-20j,   1.613e-18 +5.238e-17j,   1.613e-18 -5.238e-17j],
                       [ -3.463e-03 +7.983e-20j,  -3.463e-03 -7.983e-20j,   1.691e-18 +1.370e-16j,   1.691e-18 -1.370e-16j],
                       [  6.615e-16 -4.932e-19j,   6.615e-16 +4.932e-19j,  -1.563e-17 -3.800e-03j,  -1.563e-17 +3.800e-03j],
                       [ -4.700e-17 +3.504e-20j,  -4.700e-17 -3.504e-20j,   3.001e-17 +2.699e-04j,   3.001e-17 -2.699e-04j],
                       [ -2.394e-04 +4.508e-21j,  -2.394e-04 -4.508e-21j,   4.834e-18 -5.179e-17j,   4.834e-18 +5.179e-17j],
                       [ -3.224e-03 +6.921e-20j,  -3.224e-03 -6.921e-20j,   4.506e-18 +1.193e-16j,   4.506e-18 -1.193e-16j],
                       [  6.211e-16 -4.631e-19j,   6.211e-16 +4.631e-19j,  -1.799e-17 -3.567e-03j,  -1.799e-17 +3.567e-03j],
                       [  3.743e-16 -2.791e-19j,   3.743e-16 +2.791e-19j,   9.757e-18 -2.150e-03j,   9.757e-18 +2.150e-03j],
                       [  2.167e-03 -5.888e-20j,   2.167e-03 +5.888e-20j,   2.154e-18 -9.755e-17j,   2.154e-18 +9.755e-17j],
                       [ -2.426e-03 +5.395e-20j,  -2.426e-03 -5.395e-20j,   3.628e-18 +8.559e-17j,   3.628e-18 -8.559e-17j],
                       [  4.824e-16 -3.596e-19j,   4.824e-16 +3.596e-19j,  -3.232e-17 -2.771e-03j,  -3.232e-17 +2.771e-03j],
                       [  6.978e-16 -5.203e-19j,   6.978e-16 +5.203e-19j,  -8.435e-18 -4.008e-03j,  -8.435e-18 +4.008e-03j],
                       [  4.011e-03 -9.307e-20j,   4.011e-03 +9.307e-20j,  -2.427e-18 -1.435e-16j,  -2.427e-18 +1.435e-16j],
                       [ -1.316e-03 +3.508e-20j,  -1.316e-03 -3.508e-20j,   9.714e-19 +4.506e-17j,   9.714e-19 -4.506e-17j],
                       [  2.892e-16 -2.156e-19j,   2.892e-16 +2.156e-19j,  -1.356e-17 -1.661e-03j,  -1.356e-17 +1.661e-03j],
                       [  8.080e-16 -6.025e-19j,   8.080e-16 +6.025e-19j,  -2.083e-17 -4.641e-03j,  -2.083e-17 +4.641e-03j],
                       [  4.639e-03 -1.428e-19j,   4.639e-03 +1.428e-19j,  -8.017e-18 -1.683e-16j,  -8.017e-18 +1.683e-16j],
                       [ -1.296e-23 +9.993e-02j,  -1.296e-23 -9.993e-02j,   5.034e-15 +2.212e-17j,   5.034e-15 -2.212e-17j],
                       [ -1.489e-17 -2.194e-14j,  -1.489e-17 +2.194e-14j,  -1.202e-01 -4.117e-16j,  -1.202e-01 +4.117e-16j],
                       [  4.820e-17 +7.101e-14j,   4.820e-17 -7.101e-14j,   3.890e-01 -4.097e-16j,   3.890e-01 +4.097e-16j],
                       [  4.403e-22 +4.028e-01j,   4.403e-22 -4.028e-01j,   1.505e-14 -3.590e-16j,   1.505e-14 +3.590e-16j],
                       [  1.277e-22 +1.968e-01j,   1.277e-22 -1.968e-01j,   9.228e-15 -4.179e-16j,   9.228e-15 +4.179e-16j],
                       [ -2.649e-17 -3.902e-14j,  -2.649e-17 +3.902e-14j,  -2.138e-01 -7.890e-16j,  -2.138e-01 +7.890e-16j],
                       [  4.253e-17 +6.265e-14j,   4.253e-17 -6.265e-14j,   3.432e-01 -3.858e-16j,   3.432e-01 +3.858e-16j],
                       [  1.276e-22 +3.552e-01j,   1.276e-22 -3.552e-01j,   1.244e-14 -3.266e-16j,   1.244e-14 +3.266e-16j],
                       [  2.608e-22 +2.702e-01j,   2.608e-22 -2.702e-01j,   1.125e-14 -3.575e-16j,   1.125e-14 +3.575e-16j],
                       [ -3.528e-17 -5.198e-14j,  -3.528e-17 +5.198e-14j,  -2.847e-01 -4.124e-16j,  -2.847e-01 +4.124e-16j],
                       [  2.590e-17 +3.815e-14j,   2.590e-17 -3.815e-14j,   2.090e-01 -1.071e-15j,   2.090e-01 +1.071e-15j],
                       [ -5.880e-23 +2.154e-01j,  -5.880e-23 -2.154e-01j,   4.324e-15 -1.180e-16j,   4.324e-15 +1.180e-16j],
                       [  6.259e-22 +3.001e-01j,   6.259e-22 -3.001e-01j,   1.132e-14 -2.655e-16j,   1.132e-14 +2.655e-16j],
                       [ -3.891e-17 -5.733e-14j,  -3.891e-17 +5.733e-14j,  -3.141e-01 -3.203e-17j,  -3.141e-01 +3.203e-17j],
                       [  2.764e-18 +4.073e-15j,   2.764e-18 -4.073e-15j,   2.231e-02 -1.418e-15j,   2.231e-02 +1.418e-15j],
                       [ -9.563e-23 +2.074e-02j,  -9.563e-23 -2.074e-02j,  -4.281e-15 +1.484e-16j,  -4.281e-15 -1.484e-16j],
                       [ -2.147e-22 +2.794e-01j,  -2.147e-22 -2.794e-01j,   9.875e-15 -2.726e-16j,   9.875e-15 +2.726e-16j],
                       [ -3.653e-17 -5.382e-14j,  -3.653e-17 +5.382e-14j,  -2.948e-01 +4.481e-16j,  -2.948e-01 -4.481e-16j],
                       [ -2.202e-17 -3.244e-14j,  -2.202e-17 +3.244e-14j,  -1.777e-01 -1.334e-15j,  -1.777e-01 +1.334e-15j],
                       [ -1.264e-22 -1.877e-01j,  -1.264e-22 +1.877e-01j,  -8.073e-15 +8.601e-17j,  -8.073e-15 -8.601e-17j],
                       [  2.541e-22 +2.102e-01j,   2.541e-22 -2.102e-01j,   7.082e-15 -2.242e-16j,   7.082e-15 +2.242e-16j],
                       [ -2.837e-17 -4.180e-14j,  -2.837e-17 +4.180e-14j,  -2.290e-01 +6.707e-16j,  -2.290e-01 -6.707e-16j],
                       [ -4.104e-17 -6.047e-14j,  -4.104e-17 +6.047e-14j,  -3.313e-01 -7.048e-16j,  -3.313e-01 +7.048e-16j],
                       [ -4.908e-22 -3.476e-01j,  -4.908e-22 +3.476e-01j,  -1.187e-14 +3.158e-16j,  -1.187e-14 -3.158e-16j],
                       [  1.023e-22 +1.141e-01j,   1.023e-22 -1.141e-01j,   3.718e-15 -9.254e-17j,   3.718e-15 +9.254e-17j],
                       [ -1.701e-17 -2.506e-14j,  -1.701e-17 +2.506e-14j,  -1.373e-01 +5.962e-16j,  -1.373e-01 -5.962e-16j],
                       [ -4.753e-17 -7.002e-14j,  -4.753e-17 +7.002e-14j,  -3.836e-01 -2.575e-16j,  -3.836e-01 +2.575e-16j],
                       [ -1.956e-22 -4.020e-01j,  -1.956e-22 +4.020e-01j,  -1.390e-14 +5.053e-16j,  -1.390e-14 -5.053e-16j]])

    rotor3_evals, rotor3_evects = rotor3._eigen(sorted_=False)
    mac1 = MAC_modes(evects, rotor3_evects[:, :4], plot=False)
    # evectors order when sorted is false seems to change depending on system
    # MAC below resulted from trying to test. See how MAC~1 is not in the diag.
    # This test may have to be skipped for now
    # [[4.75627510e-25   4.75365830e-25   9.99999988e-01   9.99467499e-01]
    #  [4.75365830e-25   4.75627510e-25   9.99467499e-01   9.99999988e-01]
    # [9.99999989e-01    9.99414618e-01    7.43459739e-25    7.43174872e-25]
    # [9.99414618e-01   9.99999989e-01   7.431...
    assert_allclose(mac1.diagonal(), np.ones_like(mac1.diagonal()))


def test_kappa_rotor3(rotor3):
    assert_allclose(rotor3.kappa(0, 0)['Frequency'], 82.653037, rtol=1e-3)
    assert_allclose(rotor3.kappa(0, 0)['Major axes'], 0.001454062985920231, rtol=1e-3)
    assert_allclose(rotor3.kappa(0, 0)['Minor axes'], 2.0579515874459978e-11, rtol=1e-3, atol=1e-6)
    assert_allclose(rotor3.kappa(0, 0)['kappa'], -1.415311171090584e-08, rtol=1e-3, atol=1e-6)

    rotor3.w = 2000
    assert_allclose(rotor3.kappa(0, 0)['Frequency'], 77.37957042, rtol=1e-3)
    assert_allclose(rotor3.kappa(0, 0)['Major axes'], 0.0011885396330204021, rtol=1e-3)
    assert_allclose(rotor3.kappa(0, 0)['Minor axes'], 0.0007308144427338161, rtol=1e-3)
    assert_allclose(rotor3.kappa(0, 0)['kappa'], -0.6148843693807821, rtol=1e-3)

    assert_allclose(rotor3.kappa(0, 1)['Frequency'], 88.98733511566752, rtol=1e-3)
    assert_allclose(rotor3.kappa(0, 1)['Major axes'], 0.0009947502339267566, rtol=1e-3)
    assert_allclose(rotor3.kappa(0, 1)['Minor axes'], 0.0008412470069506472, rtol=1e-3)
    assert_allclose(rotor3.kappa(0, 1)['kappa'], 0.8456866641084784, rtol=1e-3)

    assert_allclose(rotor3.kappa(1, 1)['Frequency'], 88.98733511566752, rtol=1e-3)
    assert_allclose(rotor3.kappa(1, 1)['Major axes'], 0.0018877975750108973, rtol=1e-3)
    assert_allclose(rotor3.kappa(1, 1)['Minor axes'], 0.0014343257484060105, rtol=1e-3)
    assert_allclose(rotor3.kappa(1, 1)['kappa'], 0.7597878964314968, rtol=1e-3)


def test_kappa_mode_rotor3(rotor3):
    rotor3.w = 2000
    assert_allclose(rotor3.kappa_mode(0), [-0.614884,
                                           -0.696056,
                                           -0.723983,
                                           -0.729245,
                                           -0.708471,
                                           -0.656976,
                                           -0.513044], rtol=1e-3)

    assert_allclose(rotor3.kappa_mode(1), [0.845687,
                                           0.759788,
                                           0.734308,
                                           0.737393,
                                           0.778295,
                                           0.860137,
                                           0.948157], rtol=1e-3)


@pytest.fixture
def rotor4():
    #  Rotor without damping with 6 shaft elements 2 disks and 2 bearings
    #  Same as rotor3, but constructed with sections.
    i_d = 0
    o_d = 0.05
    n = 6
    L = [0.25 for _ in range(n)]

    n0 = len(L)//2
    n1 = len(L)//2
    L0 = sum(L[:n0])
    L1 = sum(L[n1:])
    sec0 = ShaftElement.section(L0, n0, i_d, o_d, steel)
    sec1 = ShaftElement.section(L1, n1, i_d, o_d, steel)

    shaft_elem = [sec0, sec1]

    disk0 = DiskElement(2, steel, 0.07, 0.05, 0.28)
    disk1 = DiskElement(4, steel, 0.07, 0.05, 0.35)

    stfx = 1e6
    stfy = 0.8e6
    bearing0 = BearingElement(0, kxx=stfx, kyy=stfy, cxx=0)
    bearing1 = BearingElement(6, kxx=stfx, kyy=stfy, cxx=0)

    return Rotor(shaft_elem, [disk0, disk1], [bearing0, bearing1])


def test_evals_rotor3_rotor4(rotor3, rotor4):
    rotor3_evals, rotor3_evects = rotor3._eigen()
    rotor4_evals, rotor4_evects = rotor4._eigen()

    assert_allclose(rotor3_evals, rotor4_evals, rtol=1e-3)


def test_campbell(rotor4):
    speed = np.linspace(0, 300, 3)
    camp = rotor4.campbell(speed, plot=False)
    camp_desired = np.array([[82.65303734, 82.60929602, 82.48132723],
                             [86.65811435, 86.68625235, 86.76734307],
                             [254.52047828, 251.70037114, 245.49092844],
                             [274.31285391, 276.87787937, 282.33294699],
                             [679.48903239, 652.85679897, 614.05536277],
                             [716.7863122, 742.60864608, 779.07778334]])
    assert_allclose(camp, camp_desired)


@pytest.fixture()
def rotor5():
    rotor_file = os.path.join(test_dir, 'data/xl_rotor.xls')
    bearing_file = os.path.join(test_dir, 'data/xl_bearing.xls')

    shaft = ShaftElement.load_from_xltrc(rotor_file)

    bearing0 = BearingElement.load_from_xltrc(8, bearing_file)
    bearing1 = BearingElement.load_from_xltrc(49, bearing_file)
    bearings = [bearing0, bearing1]

    disks = LumpedDiskElement.load_from_xltrc(rotor_file)

    return Rotor(shaft, disks, bearings)


def test_loaded_rotor(rotor5):
    assert len(rotor5.nodes) == 58
    assert len(rotor5.nodes_i_d) == 58
    assert len(rotor5.nodes_o_d) == 58
    assert rotor5.m_disks == 56.789932462458424
    assert rotor5.m_shaft == 190.08045208234347
    assert rotor5.m == 246.87038454480188
    assert rotor5.L == 1.65325


#  TODO implement more tests using a simple rotor with 2 elements and one disk
#  TODO add test for damped case
#  TODO add test to check wn from a rotor imported from xl

