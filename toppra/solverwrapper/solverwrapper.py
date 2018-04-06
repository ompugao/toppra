import numpy as np


class SolverWrapper(object):
    """ Base class for all solver wrappers.

    Solver wrappers are used only for implementing Reachability-based parameterization algorithms.
    The main public interface of this class is the method `solve_stagewise_optim`, which needs to
    be implemented by derived classes.

    Attributes
    ----------
    constraints : list of `Constraint`
        Constraints on the system.
    path : Interpolator
    path_discretization: array
    """

    def __init__(self, constraint_list, path, path_discretization):
        # Main attributes
        self.constraints = constraint_list
        self.path = path
        self.path_discretization = np.array(path_discretization)
        # End main attributes
        self.N = len(path_discretization) - 1  # Number of stages. Number of point is _N + 1
        self.deltas = self.path_discretization[1:] - self.path_discretization[:-1]
        assert path.get_path_interval()[0] == path_discretization[0]
        assert path.get_path_interval()[1] == path_discretization[-1]
        for i in range(self.N):
            assert path_discretization[i + 1] > path_discretization[i]

        self.params = [c.compute_constraint_params(self.path, self.path_discretization)
                       for c in self.constraints]
        self.nV = 2 + sum([c.get_no_extra_vars() for c in self.constraints])

    def get_no_stages(self):
        """ Return the number of stages.

        The number of gridpoints equals N + 1, where N is the number of stages.
        """
        return self.N

    def get_no_vars(self):
        """ Return total number of variables, including u, x.
        """
        return self.nV

    def get_deltas(self):
        return self.deltas

    def solve_stagewise_optim(self, i, H, g, x_min, x_max, x_next_min, x_next_max):
        """ Solve a stage-wise quadratic optimization.

        Parameters
        ----------
        i: int
            The stage index.
        H: array or None
            If is None, use the zero matrix.
        g: array
        x_min: float or None
        x_max: float or None
        x_next_min: float or None
        x_next_max: float or None

        Returns
        -------
        array or None
             If the optimization successes, return an array containing the optimal variable.
             Otherwise, a list of None that has the same shape as the variable.

        Notes
        -----
        This is the main public interface of `SolverWrapper`. The stage-wise quadratic optimization problem
        is given by:

        .. math::
            \\text{min  }  & 0.5 [u, x, v] H [u, x, v]^\\top + [u, x, v] g    \\\\
            \\text{s.t.  } & [u, x] \\text{ is feasible at stage } i \\\\
                           & x_{min} \leq x \leq x_{max}             \\\\
                           & x_{next, min} \leq x + 2 \Delta_i u \leq x_{next, max},

        where `v` is an auxiliary variable, only presented in non-canonical constraints.
        """
        raise NotImplementedError