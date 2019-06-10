__version__ = "1.0.0"
"""
:mod:`access` --- Accessibility Metrics
=================================================
"""

from . import fca

class access():
    """
    Spatial accessibility class.

    Parameters
    ----------
    df                   : pandas.DataFrame
                           Dataframe with three columns: origin, destination, and cost between them.
    origins              : string
                           Name of origin column
    destinations         : string
                           Name of destination column
    cost                 : string
                           Name of cost column

    Attributes
    ----------

    origins              : Name of origin column

    Methods
    -------

    fca()                : Calculate the floating catchment area (buffer) access score.


    Examples
    --------
    >>> from access import access
    >>> access().fca()
    10
    """

    def __init__(self):

        pass

    @classmethod
    def from_points(x, y):
        """
        Alternative constructor.
        """
        pass

    def fca(self, max_cost):
        """
        Calculate floating catchment 

        Parameters
        ----------
        max_cost            : float
                              Cutoff of cost values

        Returns
        -------

        access              : pandas Series
                              Accessibility score for origin locations.

        """
        
        # Merge 

        return fca.fca()


