# geometry.py — cable geometry generation, section properties, and node masses
from __future__ import annotations
import math
import numpy as np


class CableGeometry:
    """Build cable geometry from a config dict.

    Reads:
      config['geometry'] : type, L, Sag, discretisation
      config['material'] : Dia, ro, E, G, optional self_weight_N_per_m
      config['analysis'] : multiplier_mass
    """

    G_ACCEL = 9.80665  # m/s²

    def __init__(self, config: dict) -> None:
        geom = config["geometry"]
        mat = config["material"]
        ana = config["analysis"]

        self.geo_type: int = int(geom["type"])
        self.L: float = float(geom["L"])
        self.Sag: float = float(geom["Sag"])
        self.disc: float = float(geom["discretisation"])

        self.Dia: float = float(mat["Dia"])
        self.E: float = float(mat["E"])
        self.G: float = float(mat["G"])
        self.ro: float = float(mat["ro"])
        self.self_weight_source: str = "Area * ro * g"

        self.multiplier_mass: float = float(ana["multiplier_mass"])

        # --- Section properties (MATLAB correspondence) ---
        self.Area: float = math.pi * self.Dia ** 2 / 4
        self.In: float = math.pi * self.Dia ** 4 / 64
        self.Io: float = 2 * self.In
        self.ro2: float = self.Io / self.Area
        if "self_weight_N_per_m" in mat and mat["self_weight_N_per_m"] is not None:
            self.self_weight = float(mat["self_weight_N_per_m"])
            self.self_weight_source = "material.self_weight_N_per_m"
        else:
            self.self_weight = self.Area * self.ro * self.G_ACCEL  # N/m

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def generate(self) -> dict:
        """Compute and return all geometry/mass arrays.

        Returns
        -------
        dict with keys:
          x, y, z     : node coordinates (ndarray, shape (n_nodes,))
          angles       : element inclinations in radians (shape (n_nodes-1,))
          dx           : element 3-D lengths (shape (n_nodes-1,))
          DX           : tributary length at each node (shape (n_nodes,))
          MN           : translational nodal mass (shape (n_nodes,))
          MNT          : torsional nodal mass (shape (n_nodes,))
          Area, In, Io, ro2, self_weight  (scalars, passed through)
        """
        x, y, z = self._coordinates()
        angles = self._angles(x, z)
        dx = self._element_lengths(x, y, z)
        DX = self._tributary_lengths(dx)
        MN, MNT = self._masses(DX)

        return {
            "x": x,
            "y": y,
            "z": z,
            "angles": angles,
            "dx": dx,
            "DX": DX,
            "MN": MN,
            "MNT": MNT,
            "Area": self.Area,
            "In": self.In,
            "Io": self.Io,
            "ro2": self.ro2,
            "self_weight": self.self_weight,
            "self_weight_source": self.self_weight_source,
        }

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _coordinates(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        x = np.arange(0.0, self.L + self.disc / 2, self.disc)
        y = np.zeros_like(x)

        if self.geo_type == 1:          # Parabolic
            a = 4 * self.Sag / self.L ** 2
            b = -4 * self.Sag / self.L
            z = a * x ** 2 + b * x

        elif self.geo_type == 2:        # Catenary
            x1 = x - self.L / 2
            a = self._catenary_parameter()
            z1 = a * np.cosh(x1 / a)
            z = z1 - np.max(z1)

        elif self.geo_type == 3:        # Broken-line (V-shape)
            x_mid = self.L / 2
            z = np.empty_like(x)
            for i, xi in enumerate(x):
                if xi <= x_mid:
                    z[i] = -self.Sag * xi / x_mid
                else:
                    z[i] = -self.Sag * (self.L - xi) / x_mid

        else:
            raise ValueError(f"Unknown geometry type: {self.geo_type!r} (must be 1, 2, or 3)")

        return x, y, z

    def _catenary_parameter(self) -> float:
        """Solve sag = a * (cosh(L / (2a)) - 1) for the catenary parameter."""
        if self.Sag <= 0:
            raise ValueError("Catenary sag must be positive")

        def sag_from_a(a: float) -> float:
            return a * (math.cosh(self.L / (2 * a)) - 1)

        high = max(self.L**2 / (8 * self.Sag), self.L, 1.0)
        while sag_from_a(high) > self.Sag:
            high *= 2.0

        low = high / 2.0
        while sag_from_a(low) < self.Sag:
            low /= 2.0

        for _ in range(80):
            mid = (low + high) / 2.0
            if sag_from_a(mid) > self.Sag:
                low = mid
            else:
                high = mid

        return (low + high) / 2.0

    @staticmethod
    def _angles(x: np.ndarray, z: np.ndarray) -> np.ndarray:
        return np.arctan((z[1:] - z[:-1]) / (x[1:] - x[:-1]))

    @staticmethod
    def _element_lengths(
        x: np.ndarray, y: np.ndarray, z: np.ndarray
    ) -> np.ndarray:
        return np.sqrt(
            (x[1:] - x[:-1]) ** 2
            + (y[1:] - y[:-1]) ** 2
            + (z[1:] - z[:-1]) ** 2
        )

    @staticmethod
    def _tributary_lengths(dx: np.ndarray) -> np.ndarray:
        n = len(dx) + 1          # number of nodes = number of elements + 1
        DX = np.empty(n)
        DX[0] = dx[0] / 2
        DX[-1] = dx[-1] / 2
        DX[1:-1] = (dx[:-1] + dx[1:]) / 2
        return DX

    def _masses(self, DX: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        g = self.G_ACCEL
        MN = DX * self.self_weight / g * self.multiplier_mass
        MNT = self.ro2 * DX * self.self_weight / g * self.multiplier_mass
        return MN, MNT
