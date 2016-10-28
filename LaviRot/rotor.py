import numpy as np
import scipy.linalg as la
from LaviRot.elements import *


class Rotor(object):
    """A rotor object.

    This class will create a rotor with the shaft,
    disk and bearing elements provided.

    Parameters
    ----------
    shaft_elements: list
        List with the shaft elements
    disk_elements: list
        List with the disk elements
    bearing_elements: list
        List with the bearing elements

    Returns
    -------
    A rotor object.

    Examples
    >>> #  Rotor without damping with 2 shaft elements 1 disk and 2 bearings
    >>> n = 1
    >>> z = 0
    >>> le = 0.25
    >>> i_d = 0
    >>> o_d = 0.05
    >>> E = 211e9
    >>> G = 81.2e9
    >>> rho = 7810
    >>> tim0 = ShaftElement(0, 0.0, le, i_d, o_d, E, G, rho,
    ...                    shear_effects=True,
    ...                    rotary_inertia=True,
    ...                    gyroscopic=True)
    >>> tim1 = ShaftElement(1, 0.25, le, i_d, o_d, E, G, rho,
    ...                    shear_effects=True,
    ...                    rotary_inertia=True,
    ...                    gyroscopic=True)
    >>> shaft_elm = [tim0, tim1]
    >>> disk0 = DiskElement(1, rho, 0.07, 0.05, 0.28)
    >>> stf = 1e6
    >>> bearing0 = BearingElement(0, stf, stf, 0, 0)
    >>> bearing1 = BearingElement(2, stf, stf, 0, 0)
    >>> rotor = Rotor(shaft_elm, [disk0], [bearing0, bearing1])
    >>> rotor.wd
    array([  34.27731557,   34.27731557,   95.17859364,   95.17859364,
            629.65276153,  629.65276153])
    """

    def __init__(self, shaft_elements, disk_elements, bearing_elements, w=0):
        #  TODO consider speed as a rotor property. Setter should call __init__ again
        self._w = w
        self.shaft_elements = shaft_elements
        self.bearing_elements = bearing_elements
        self.disk_elements = disk_elements
        # Values for evalues and evectors will be calculated by self._calc_system
        self.evalues = None
        self.evectors = None
        self.wn = None
        self.wd = None
        #  TODO check when disk diameter in no consistent with shaft diameter
        #  TODO add error for elements added to the same n (node)
        # number of dofs
        self.ndof = 4 * len(shaft_elements) + 4

        #  nodes axial position
        nodes_pos = [s.z for s in self.shaft_elements]
        # append position for last node
        nodes_pos.append(self.shaft_elements[-1].z
                         + self.shaft_elements[-1].L)
        self.nodes_pos = nodes_pos
        self.nodes = [i for i in range(len(self.nodes_pos))]

        #  TODO for tappered elements i_d and o_d will be a list with two elements
        #  diameter at node position
        nodes_i_d = [s.i_d for s in self.shaft_elements]
        # append i_d for last node
        nodes_i_d.append(self.shaft_elements[-1].i_d)
        self.nodes_i_d = nodes_i_d

        nodes_o_d = [s.o_d for s in self.shaft_elements]
        # append o_d for last node
        nodes_o_d.append(self.shaft_elements[-1].o_d)
        self.nodes_o_d = nodes_o_d

        # call self._calc_system() to calculate current evalues and evectors
        self._calc_system()

    def _calc_system(self):
        self.evalues, self.evectors = self._eigen(self._w)
        self.wn = (np.absolute(self.evalues)/(2*np.pi))[:self.ndof//2]
        self.wd = (np.imag(self.evalues)/(2*np.pi))[:self.ndof//2]

    @property
    def w(self):
        return self._w

    @w.setter
    def w(self, value):
        self._w = value
        self._calc_system()

    @staticmethod
    def _dofs(element):
        """The first and last dof for a given element"""
        if type(element).__name__ == 'ShaftElement':
            node = element.n
            n1 = 4 * node
            n2 = n1 + 8
        if type(element).__name__ == 'DiskElement':
            node = element.n
            n1 = 4 * node
            n2 = n1 + 4
        if type(element).__name__ == 'BearingElement':
            node = element.n
            n1 = 4 * node
            n2 = n1 + 2
        # TODO implement this for bearing with more dofs
        return n1, n2

    def M(self):
        """This method returns the rotor mass matrix"""
        #  Create the matrices
        M0 = np.zeros((self.ndof, self.ndof))

        for elm in self.shaft_elements:
            n1, n2 = self._dofs(elm)
            M0[n1:n2, n1:n2] += elm.M()

        for elm in self.disk_elements:
            n1, n2 = self._dofs(elm)
            M0[n1:n2, n1:n2] += elm.M()

        return M0

    def K(self):
        """This method returns the rotor stiffness matrix"""
        #  Create the matrices
        K0 = np.zeros((self.ndof, self.ndof))

        for elm in self.shaft_elements:
            n1, n2 = self._dofs(elm)
            K0[n1:n2, n1:n2] += elm.K()

        for elm in self.bearing_elements:
            n1, n2 = self._dofs(elm)
            K0[n1:n2, n1:n2] += elm.K()
        #  Skew-symmetric speed dependent contribution to element stiffness matrix
        #  from the internal damping.
        #  TODO add the contribution for K1 matrix

        return K0

    def C(self):
        """This method returns the rotor stiffness matrix"""
        #  Create the matrices
        C0 = np.zeros((self.ndof, self.ndof))

        for elm in self.bearing_elements:
            n1, n2 = self._dofs(elm)
            C0[n1:n2, n1:n2] += elm.C()

        return C0

    def G(self):
        """This method returns the rotor stiffness matrix"""
        #  Create the matrices
        G0 = np.zeros((self.ndof, self.ndof))

        for elm in self.shaft_elements:
            n1, n2 = self._dofs(elm)
            G0[n1:n2, n1:n2] += elm.G()

        for elm in self.disk_elements:
            n1, n2 = self._dofs(elm)
            G0[n1:n2, n1:n2] += elm.G()

        return G0

    def A(self, w=0):
        """This method creates a speed dependent space state matrix"""
        Z = np.zeros((self.ndof, self.ndof))
        I = np.eye(self.ndof)
        Minv = la.pinv(self.M())
        #  TODO implement K(w) and C(w) for shaft, bearings etc.
        A = np.vstack([np.hstack([Z, I]),
                       np.hstack([-Minv @ self.K(), -Minv @ (self.C() + self.G()*w)])])

        return A

    @staticmethod
    def _index(eigenvalues):
        r"""Function used to generate an index that will sort
        eigenvalues and eigenvectors based on the imaginary (wd)
        part of the eigenvalues. Positive eigenvalues will be
        positioned at the first half of the array.

        Parameters
        ----------
        eigenvalues: array
            Array with the eigenvalues.

        Returns
        -------
        idx:
            An array with indices that will sort the
            eigenvalues and eigenvectors.

        Examples:
        >>> rotor = rotor_example()
        >>> evalues, evectors = rotor._eigen(0, sorted_=False)
        >>> idx = rotor._index(evalues)
        >>> idx[:6]
        array([22, 20, 16, 18, 12, 14], dtype=int64)
        """
        # positive in increasing order
        idxp = eigenvalues.imag.argsort()[int(len(eigenvalues)/2):]
        # negative in decreasing order
        idxn = eigenvalues.imag.argsort()[int(len(eigenvalues)/2) - 1::-1]

        idx = np.hstack([idxp, idxn])

        #  TODO implement sort that considers the cross of eigenvalues
        return idx

    def _eigen(self, w=0, sorted_=True):
        r"""This method will return the eigenvalues and eigenvectors of the
        state space matrix A, sorted by the index method which considers
        the imaginary part (wd) of the eigenvalues for sorting.
        To avoid sorting use sorted_=False

        Parameters
        ----------
        w: float
            Rotor speed.

        Returns
        -------
        evalues: array
            An array with the eigenvalues
        evectors array
            An array with the eigenvectors

        Examples:
        >>> rotor = rotor_example()
        >>> evalues, evectors = rotor._eigen(0)
        >>> evalues[:2]
        array([ -6.81898982e-13+215.37072557j,   2.13731810e-12+215.37072557j])
        """
        evalues, evectors = la.eig(self.A(w))
        if sorted_ is False:
            return evalues, evectors

        idx = self._index(evalues)

        return evalues[idx], evectors[:, idx]

    # TODO separate kappa-create a function that will return lam and U (extract method)
    def kappa(self, node, w, wd=True):
        """
        w is the the index of the natural frequency of interest
        This function calculates the matrix
         :math:
         T = ...
         and the matrix :math: H = T.T^T for a given node.
         The eigenvalues of H correspond to the minor and
         major axis of the orbit.
        """
        if wd:
            nat_freq = self.wd[w]
        else:
            nat_freq = self.wn[w]

        # get mode of interest based on freqs
        mode = self.evectors[4*node:4*node+2, w]
        # get translation sdofs for specified node for each mode
        u = mode[0]
        v = mode[1]
        ru = np.absolute(u)
        rv = np.absolute(v)
        if ru*rv < 1e-16:
            k = ({'Frequency': nat_freq,
                  'Minor axes': 0,
                  'Major axes': 0,
                  'kappa': 0})
            return k

        nu = np.angle(u)
        nv = np.angle(v)
        T = np.array([[ru * np.cos(nu), -ru * np.sin(nu)],
                      [rv * np.cos(nv), -rv * np.sin(nv)]])
        H = T @ T.T

        lam = la.eig(H)[0]

        #  TODO normalize the orbit (after all orbits have been calculated?)
        # lam is the eigenvalue -> sqrt(lam) is the minor/major axis.
        # kappa encodes the relation between the axis and the precession.
        minor = np.sqrt(lam.min())
        major = np.sqrt(lam.max())
        kappa = minor / major
        diff = nv - nu

        # we need to evaluate if 0 < nv - nu < pi.
        if diff < -np.pi:
            diff += 2 * np.pi
        elif diff > np.pi:
            diff -= 2 * np.pi

        # if nv = nu or nv = nu + pi then the response is a straight line.
        if diff == 0 or diff == np.pi:
            kappa = 0

        # if 0 < nv - nu < pi, then a backward rotating mode exists.
        elif 0 < diff < np.pi:
            kappa *= -1

        k = ({'Frequency': nat_freq,
              'Minor axes': np.real(minor),
              'Major axes': np.real(major),
              'kappa': np.real(kappa)})

        return k

    def kappa_mode(self, w):
        r"""This function evaluates kappa for a given the index of
        the natural frequency of interest.
        Values of kappa are evaluated for each node of the
        corresponding frequency mode.

        Parameters
        ----------
        w: int
            Index corresponding to the natural frequency
            of interest.

        Returns
        -------
        kappa_mode: list
            A list with the value of kappa for each node related
            to the mode/natural frequency of interest.

        Examples:
        >>> rotor = rotor_example()
        >>> # kappa for each node of the first natural frequency
        >>> rotor.kappa_mode(0)
        [array(-0.03144693759930626), array(-0.03144693759930822), array(-0.03144693759930619)]
        """
        kappa_mode = [self.kappa(node, w)['kappa'] for node in self.nodes]
        return kappa_mode


    def orbit(self):
        pass
    #  TODO make w a property. Make eigen an attribute.
    #  TODO when w is changed, eigen is calculated and is available to methods.
    #  TODO static methods as auxiliary functions


def rotor_example():
    r"""This function returns an instance of a simple rotor with
    two shaft elements, one disk and two simple bearings.
    The purpose of this is to make available a simple model
    so that doctest can be written using this.

    Parameters
    ----------

    Returns
    -------
    An instance of a rotor object.

    Examples:
    >>> rotor = rotor_example()
    >>> rotor.wd
    array([  34.27731557,   34.27731557,   95.17859364,   95.17859364,
            629.65276153,  629.65276153])
    """

    #  Rotor without damping with 2 shaft elements 1 disk and 2 bearings
    n = 1
    z = 0
    le = 0.25
    i_d = 0
    o_d = 0.05
    E = 211e9
    G = 81.2e9
    rho = 7810

    tim0 = ShaftElement(0, 0.0, le, i_d, o_d, E, G, rho,
                        shear_effects=True,
                        rotary_inertia=True,
                        gyroscopic=True)
    tim1 = ShaftElement(1, 0.25, le, i_d, o_d, E, G, rho,
                        shear_effects=True,
                        rotary_inertia=True,
                        gyroscopic=True)

    shaft_elm = [tim0, tim1]
    disk0 = DiskElement(1, rho, 0.07, 0.05, 0.28)
    stf = 1e6
    bearing0 = BearingElement(0, stf, stf, 0, 0)
    bearing1 = BearingElement(2, stf, stf, 0, 0)
    return Rotor(shaft_elm, [disk0], [bearing0, bearing1])
