.. _api_ref:

.. currentmodule:: access

API reference
=============

If you're just getting started, have a look at :mod:`access.access`
(or the :ref:`tutorials`!)
to see the basic structure of the package and its applications.

Accessibility Class
----------------------
.. autoclass:: access
   :members:
   :toctree: generated/

.. autosummary::
   :toctree: generated/
   
    access.access
    access.access.weighted_catchment
    access.access.fca_ratio
    access.access.two_stage_fca
    access.access.enhanced_two_stage_fca
    access.access.three_stage_fca
    access.access.raam
    access.access.score
    access.access.create_euclidean_distance
    access.access.create_euclidean_distance_neighbors
    access.access.append_user_cost
    access.access.append_user_cost_neighbors

Helper Functions
----------------

.. autosummary::
   :toctree: generated/

    access.weights.step_fn
    access.weights.gravity
    access.weights.gaussian

Internal Access Functions
-------------------------

The access class uses lower-level functions for its internal calculations.
In most cases, we do not expect users to call these directly.
However, users seeking to understand these calculations and their inputs
can still consult the :ref:`afunctions`.
