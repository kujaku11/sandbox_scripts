from melt_physics_workflow import (
    MeltConductivityModel, ModifiedArchieModel, ElasticAggregate,
    SeismicMeltReduction, JointMeltEstimator
)

def test_forward_basic():
    melt_cond = MeltConductivityModel()
    archie = ModifiedArchieModel()
    elastic = ElasticAggregate(125.0, 75.0, 3300.0)
    seismic = SeismicMeltReduction()
    estimator = JointMeltEstimator(melt_cond, archie, elastic, seismic)

    T_K = 1473.0
    comp = {"H2O": 2.0, "CO2": 0.2}
    out = estimator.forward(phi=0.05, T_K=T_K, comp=comp)
    assert "sigma_bulk" in out and "vp_ms" in out
    assert out["rho_bulk_Ohm_m"] > 0