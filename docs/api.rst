.. _api_ref:

API reference
=============

If you're just getting started, have a look at :mod:`access.access` or :ref:`access_class` (or the :ref:`tutorials`!)
to see the basic structure of the package and its applications.

.. currentmodule:: access

Accessibility Class
----------------------
For the full definitions and examples of each method, see individual functions..

.. autosummary::
   :toctree: generated/
   
    access
    access.weighted_catchment
    access.fca_ratio
    access.two_stage_fca
    access.enhanced_two_stage_fca
    access.three_stage_fca
    access.raam
    access.score
    access.create_euclidean_distance
    access.create_euclidean_distance_neighbors
    access.append_user_cost
    access.append_user_cost_neighbors


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
