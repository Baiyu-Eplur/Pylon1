from __future__ import annotations

import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "output" / "diagnostics" / "typical_incremental_quasi_steady_formal_no_stop"
MONITOR_DIR = CASE_DIR / "point_monitoring"
FORCE_DIR = ROOT / "data" / "forces" / "FORCE_3" / "SIM1"

RHO = 1.293
B = 0.02862
TRIBUTARY = {
    26: 3.23479091521,
    51: 3.22800271433,
    76: 3.23425854844,
}


def main() -> None:
    files = [
        ("quarter_1", 26, MONITOR_DIR / "quarter_1_node_26_timeseries.csv"),
        ("midspan", 51, MONITOR_DIR / "midspan_node_51_timeseries.csv"),
        ("quarter_3", 76, MONITOR_DIR / "quarter_3_node_76_timeseries.csv"),
    ]
    windows = [(0, 50), (50, 58), (58, 65), (65, 75), (75, 86.44)]
    header = (
        "point,window,p_current_mean_W,p_current_positive_fraction,"
        "p_delta_mean_W,p_delta_positive_fraction,p_drag_mean_W,p_lift_mean_W,"
        "max_Urel_mps,max_alpha_unclipped_deg"
    )
    print(header)
    for name, node, path in files:
        arr = np.genfromtxt(path, delimiter=",", names=True)
        t = arr["time_s"]
        vx = arr["vel_transverse_x_mps"]
        vz = arr["vel_vertical_z_mps"]
        wx = arr["wind_x_mps"]
        wz = arr["wind_z_mps"]
        relx = wx - vx
        relz = wz - vz
        u_rel = np.sqrt(relx**2 + relz**2)
        ex = np.divide(relx, u_rel, out=np.zeros_like(u_rel), where=u_rel > 1e-12)
        ez = np.divide(relz, u_rel, out=np.zeros_like(u_rel), where=u_rel > 1e-12)
        q_area = 0.5 * RHO * u_rel**2 * (math.pi * B * TRIBUTARY[node] / 2.0)
        cd = arr["C_D"]
        cl = arr["C_L"]
        drag_x = q_area * cd * ex
        drag_z = q_area * cd * ez
        lift_x = -q_area * cl * ez
        lift_z = q_area * cl * ex
        current_x = drag_x + lift_x
        current_z = drag_z + lift_z
        p_current = current_x * vx + current_z * vz
        p_drag = drag_x * vx + drag_z * vz
        p_lift = lift_x * vx + lift_z * vz

        h_drag = 1000.0 * np.loadtxt(FORCE_DIR / f"NODE_{node}_H_drag.txt", max_rows=len(t))
        h_lift = 1000.0 * np.loadtxt(FORCE_DIR / f"NODE_{node}_H_lift.txt", max_rows=len(t))
        v_drag = 1000.0 * np.loadtxt(FORCE_DIR / f"NODE_{node}_V_drag.txt", max_rows=len(t))
        v_lift = 1000.0 * np.loadtxt(FORCE_DIR / f"NODE_{node}_V_lift.txt", max_rows=len(t))
        reference_x = h_drag + v_lift
        reference_z = h_lift + v_drag
        p_delta = (current_x - reference_x) * vx + (current_z - reference_z) * vz

        alpha = arr["alpha_lookup_deg_unclipped"]
        for start, end in windows:
            mask = (t >= start) & (t < end)
            if not np.any(mask):
                continue
            print(
                ",".join(
                    [
                        name,
                        f"{start}-{end}",
                        f"{np.mean(p_current[mask]):.6g}",
                        f"{np.mean(p_current[mask] > 0):.3f}",
                        f"{np.mean(p_delta[mask]):.6g}",
                        f"{np.mean(p_delta[mask] > 0):.3f}",
                        f"{np.mean(p_drag[mask]):.6g}",
                        f"{np.mean(p_lift[mask]):.6g}",
                        f"{np.max(u_rel[mask]):.3f}",
                        f"{np.max(alpha[mask]):.2f}",
                    ]
                )
            )

    print("")
    print("static_baseline_check,node,mean_abs_delta_N,max_abs_delta_N,mean_ref_abs_N,mean_ratio")
    for node in (26, 51, 76):
        wind_h = np.loadtxt(FORCE_DIR / f"NODE_{node}_wind_H.txt")
        wind_v = np.loadtxt(FORCE_DIR / f"NODE_{node}_wind_V.txt")
        h_drag = 1000.0 * np.loadtxt(FORCE_DIR / f"NODE_{node}_H_drag.txt")
        h_lift = 1000.0 * np.loadtxt(FORCE_DIR / f"NODE_{node}_H_lift.txt")
        v_drag = 1000.0 * np.loadtxt(FORCE_DIR / f"NODE_{node}_V_drag.txt")
        v_lift = 1000.0 * np.loadtxt(FORCE_DIR / f"NODE_{node}_V_lift.txt")
        ref_y = h_drag + v_lift
        ref_z = h_lift + v_drag

        # Reconstruct the coefficients from force components, then recompute the
        # current implementation's zero-motion force decomposition.
        u_ref = np.sqrt(wind_h**2 + wind_v**2)
        area = math.pi * B * TRIBUTARY[node] / 2.0
        q_area = 0.5 * RHO * u_ref**2 * area
        ey = np.divide(wind_h, u_ref, out=np.zeros_like(u_ref), where=u_ref > 1e-12)
        ez = np.divide(wind_v, u_ref, out=np.zeros_like(u_ref), where=u_ref > 1e-12)
        cd = np.divide(h_drag, q_area * ey, out=np.zeros_like(q_area), where=np.abs(q_area * ey) > 1e-12)
        # wind_forces.py writes V_lift = qA * CL * cos(alpha), so this keeps the CL sign.
        cl = np.divide(v_lift, q_area * ey, out=np.zeros_like(q_area), where=np.abs(q_area * ey) > 1e-12)
        current_y = q_area * cd * ey - q_area * cl * ez
        current_z = q_area * cd * ez + q_area * cl * ey
        delta = np.sqrt((current_y - ref_y) ** 2 + (current_z - ref_z) ** 2)
        ref_abs = np.sqrt(ref_y**2 + ref_z**2)
        mask = ref_abs > 1e-12
        print(
            "static_baseline_check,{},{:.6g},{:.6g},{:.6g},{:.6g}".format(
                node,
                float(np.mean(delta)),
                float(np.max(delta)),
                float(np.mean(ref_abs)),
                float(np.mean(delta[mask] / ref_abs[mask])),
            )
        )


if __name__ == "__main__":
    main()
