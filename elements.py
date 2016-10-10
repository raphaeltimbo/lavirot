import numpy as np


class BeamElement(object):
    """A beam element.

    This class will create a shaft element that may take into
    account shear, rotary inertia an gyroscopic effects.
    The matrices will be defined considering the following local
    coordinate vector:
    [u1, v1, theta1, psi1, u2, v2, theta2, psi2].T
    Where theta1 and theta2 are the bending on the yz plane and
    psi1 and psi2 are the bending on the xz plane.

    Parameters
    ----------
    n: int
        Element number
    x1: float
        Position of the element first node
    L: float
        Element length
    i_d: float3
        Inner diameter of the element
    o_d: float
        Outer diameter of the element
    E: float
        Young's modulus
    G: float
        Shear modulus
    rho: float
        Density
    axial_force: float
        Axial force
    torque: float
        Torque
    sheaf_effects: bool
        Determine if shear effects are taken into account.
        Default is False
    rotary_inertia: bool
        Determine if rotary_inertia effects are taken into account.
        Default is False
    gyroscopic: bool
        Determine if gyroscopic effects are taken into account.
        Default is False


    Returns
    ----------
    A beam element.

    Examples:
    >>> n_ = 1
    >>> x1_ = 0
    >>> le_ = 0.25
    >>> i_d_ = 0
    >>> o_d_ = 0.05
    >>> E_ = 211e9
    >>> G_ = 81.2e9
    >>> rho_ = 7810
    >>> Euler_Bernoulli_Element = BeamElement(n_, x1_, le_, i_d_, o_d_, E_, G_, rho_)
    >>> Iimoshenko_Element = BeamElement(n_, x1_, le_, i_d_, o_d_, E_, G_, rho_,
    ...                          rotary_inertia=True,
    ...                          shear_effects=True)
    """

    def __init__(self, n, x1, L, i_d, o_d, E, G, rho,
                 axial_force=0, torque=0,
                 shear_effects=False,
                 rotary_inertia=False,
                 gyroscopic=True):

        self.shear_effects = shear_effects
        self.rotary_inertia = rotary_inertia
        self.gyroscopic = gyroscopic

        self.n = n
        self.x1 = x1
        self.L = L
        self.i_d = i_d
        self.o_d = o_d
        self.E = E
        self.G = G
        self.poisson = 0.5*(E/G) - 1
        self.rho = rho
        self.A = np.pi*(o_d**2 - i_d**2)/4
        #  Ie is the second moment of area of the cross section about
        #  the neutral plane Ie = pi*r**2/4
        self.Ie = np.pi*(o_d**4 - i_d**4)/64
        phi = 0

        if shear_effects:
            #  Shear coefficient (phi)
            r = i_d/o_d
            r2 = r*r
            r12 = (1 + r2)**2
            #  kappa as per Hutchinson (2001)
            #kappa = 6*r12*((1+self.poisson)/
            #           ((r12*(7 + 12*self.poisson + 4*self.poisson**2) +
            #             4*r2*(5 + 6*self.poisson + 2*self.poisson**2))))
            kappa = 6*r12*((1+self.poisson)/
                       ((r12*(7 + 6*self.poisson) +
                         r2*(20 + 12*self.poisson))))
            phi = 12*E*self.Ie/(G*kappa*self.A*L**2)

        self.phi = phi

        #  ========== Mass Matrix ==========

    def M(self):
        phi = self.phi
        L = self.L

        m01 = 312 + 588*phi + 280*phi**2
        m02 = (44 + 77*phi + 35*phi**2)*L
        m03 = 108 + 252*phi + 140*phi**2
        m04 = -(26 + 63*phi + 35*phi**2)*L
        m05 = (8 + 14*phi + 7*phi**2)*L**2
        m06 = -(6 + 14*phi + 7*phi**2)*L**2

        M = np.array([[m01,     0,     0,   m02,   m03,     0,     0,   m04],
                        [  0,   m01,  -m02,     0,     0,   m03,  -m04,     0],
                        [  0,  -m02,   m05,     0,     0,   m04,   m06,     0],
                        [m02,     0,     0,   m05,  -m04,     0,     0,   m06],
                        [m03,     0,     0,  -m04,   m01,     0,     0,  -m02],
                        [  0,   m03,   m04,     0,     0,   m01,   m02,     0],
                        [  0,  -m04,   m06,     0,     0,   m02,   m05,     0],
                        [m04,     0,     0,   m06,  -m02,     0,     0,   m05]])

        M = self.rho * self.A * self.L * M/(840*(1 + phi)**2)

        if self.rotary_inertia:
            ms1 = 36;
            ms2 = (3 - 15*phi)*L
            ms3 = (4 + 5*phi + 10*phi**2)*L**2
            ms4 = (-1 - 5*phi + 5*phi**2)*L**2
            Ms = np.array([[ms1,      0,     0,   ms2,  -ms1,     0,     0,   ms2],
                           [   0,   ms1,  -ms2,     0,     0,  -ms1,  -ms2,     0],
                           [   0,  -ms2,   ms3,     0,     0,   ms2,   ms4,     0],
                           [ ms2,     0,     0,   ms3,  -ms2,     0,     0,   ms4],
                           [-ms1,     0,     0,  -ms2,   ms1,     0,     0,  -ms2],
                           [   0,  -ms1,   ms2,     0,     0,   ms1,   ms2,     0],
                           [   0,  -ms2,   ms4,     0,     0,   ms2,   ms3,     0],
                           [ ms2,     0,     0,   ms4,  -ms2,     0,     0,   ms3]])

            Ms = self.rho * self.Ie * Ms/(30*L*(1 + phi)**2)
            M = M + Ms

        return M

    #  ========== Stiffness Matrix ==========

    def K(self):
        phi = self.phi
        L = self.L

        K = np.array([[12,     0,            0,          6*L,  -12,     0,            0,          6*L],
                        [0,     12,         -6*L,            0,    0,   -12,         -6*L,            0],
                        [0,   -6*L, (4+phi)*L**2,            0,    0,   6*L, (2-phi)*L**2,            0],
                        [6*L,    0,            0, (4+phi)*L**2, -6*L,     0,            0, (2-phi)*L**2],
                        [-12,    0,            0,         -6*L,   12,     0,            0,         -6*L],
                        [0,    -12,          6*L,            0,    0,    12,          6*L,            0],
                        [0,   -6*L, (2-phi)*L**2,            0,    0,   6*L, (4+phi)*L**2,            0],
                        [6*L,    0,            0, (2-phi)*L**2, -6*L,     0,            0, (4+phi)*L**2]])

        K = self.E * self.Ie * K/((1 + phi)*L**3)

        return K

    def G(self):
        phi = self.phi
        L = self.L

        G = np.zeros((8, 8))

        if self.gyroscopic:
            g1 = 36
            g2 = (3 - 15 * phi) * L
            g3 = (4 + 5 * phi + 10 * phi**2) * L**2
            g4 = (-1 - 5 * phi + 5 * phi**2) * L**2

            G = np.array([[  0,  g1,  g2,   0,   0,  g1,  g2,   0],
                            [ g1,   0,   0,  g2, -g1,   0,   0,  g2],
                            [-g2,   0,   0, -g3,  g2,   0,   0, -g4],
                            [  0, -g2,  g3,   0,   0,  g2,  g4,   0],
                            [  0,  g1, -g2,   0,   0, -g1, -g2,   0],
                            [-g1,   0,   0, -g2,  g1,   0,   0, -g2],
                            [-g2,   0,   0, -g4,  g2,   0,   0, -g3],
                            [  0, -g2,  g4,   0,   0,  g2,  g3,   0]])

            G = - self.rho * self.Ie * G / (15 * L * (1 + phi)**2)

        return G

        #  TODO Stiffness Matrix due to an axial load
        #  TODO Stiffness Matrix due to an axial torque
        #  TODO Skew-symmetric speed dependent contribution to element stiffness matrix from the internal damping.


class DiskElement(object):
    """A disk element.

    This class will create a disk element.

    Parameters
    ----------
    n: int
        Node in which the disk will be inserted
    rho: float
        Mass density
    width: float
        The disk width
    i_d: float
        Inner diameter
    o_d: float
        Outer diameter

    Returns
    ----------
    A disk element.

    Examples:

    """

    def __init__(self, rho, width, i_d, o_d):
        self.rho = rho
        self.width = width
        self.i_d = i_d
        self.o_d = o_d
        self.m = 0.25 * rho * np.pi * width * (o_d**2 - i_d**2)
        self.Id = 0.015625 * rho * np.pi * width*(o_d**4 - i_d**4) + self.m*(width**2)/12
        self.Ip = 0.03125 * rho * np.pi * width * (o_d**4 - i_d**4)

    def M(self):
        m = self.m
        Id = self.Id

        M = np.array([[m, 0,  0,  0],
                       [0, m,  0,  0],
                       [0, 0, Id,  0],
                       [0, 0,  0, Id]])

        return M

    def G(self):
        Ip = self.Ip

        G = np.array([[0, 0,   0,  0],
                       [0, 0,   0,  0],
                       [0, 0,   0, Ip],
                       [0, 0, -Ip,  0]])

        return G


class Bearing(object):
    """A bearing element.

    This class will create a bearing element.

    Parameters
    ----------
    kxx: float
        Direct stiffness in the x direction
    kyy: float
        Direct stiffness in the y direction
    cxx: float
        Direct stiffness in the x direction
    cyy: float
        Direct stiffness in the y direction

    Returns
    ----------
    A bearing element.

    Examples:

    """

    def __init__(self, kxx, kyy, cxx, cyy):
        self.kxx = kxx
        self.kyy = kyy
        self.cxx = cxx
        self.cyy = cyy

    def K(self):
        K = np.array([[kxx,   0],
                      [  0, kyy]])

        return K

    def C(self):
        C = np.array([[cxx,   0],
                      [  0, cyy]])

        return C