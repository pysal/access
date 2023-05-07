.. _api_ref:

API reference
=============

If you're just getting started, have a look at :mod:`access.Access` or :ref:`access_class` (or the :ref:`tutorials`!)
to see the basic structure of the package and its applications.

.. currentmodule:: access

Accessibility Class
----------------------
For the full definitions and examples of each method, see individual functions.

.. autosummary::
   :toctree: generated/

    Access
    Access.weighted_catchment
    Access.fca_ratio
    Access.two_stage_fca
    Access.enhanced_two_stage_fca
    Access.three_stage_fca
    Access.raam
    Access.score
    Access.create_euclidean_distance
    Access.create_euclidean_distance_neighbors
    Access.append_user_cost
    Access.append_user_cost_neighbors


Helper Functions
----------------

.. autosummary::
   :toctree: generated/

    weights.step_fn
    weights.gravity
    weights.gaussian

Internal Access Functions
-------------------------

The access class uses lower-level functions for its internal calculations.
In most cases, we do not expect users to call these directly.
However, users seeking to understand these calculations and their inputs
can still consult the :ref:`afunctions`.
