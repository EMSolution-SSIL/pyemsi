from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
import json
import numpy as np
from matplotlib.figure import Figure
from matplotlib.axes import Axes


# ── Helpers ────────────────────────────────────────────────────────────────


def _arr(lst) -> np.ndarray:
    return np.asarray(lst, dtype=float)


def _make_ax(ax: Axes | None) -> tuple[Figure, Axes]:
    """Create or reuse an Axes.

    In GUI mode (is_gui_running=True) creates a non-interactive Figure() with
    no pyplot state. In standalone mode creates via plt.subplots() so the
    caller can display via pyplot. Does not call show internally.
    """
    if ax is not None:
        return ax.figure, ax
    import pyemsi

    if pyemsi.is_gui_running():
        fig = Figure()
        return fig, fig.add_subplot(111)
    else:
        import matplotlib.pyplot as plt

        return plt.subplots()


# ── Simple containers ──────────────────────────────────────────────────────


@dataclass
class MetaData:
    version: str
    release_date: str
    creation_date: str
    comments: str


@dataclass
class AnalysisCondition:
    analysis_type: Literal["TRANSIENT", "STATIC"]
    nonlinear: Literal["LINEAR", "NONLINEAR"]
    motion_type: Literal["NONE", "SLIDE_MOTION"]
    circuit_type: Literal["CIRCUIT", "NETWORK"]


# ── Circuit ────────────────────────────────────────────────────────────────


@dataclass
class CircuitElement:
    serial_num: int
    current: np.ndarray
    voltage: np.ndarray
    flux: np.ndarray | None
    _time: np.ndarray | None = field(default=None, repr=False, compare=False, init=False)

    def plot_current(self, ax=None, x=None, **kw) -> tuple[Figure, Axes]:
        fig, ax = _make_ax(ax)
        x = x if x is not None else self._time
        if x is not None:
            ax.plot(x, self.current, **kw)
            ax.set_xlim(x[0], x[-1])
        else:
            ax.plot(self.current, **kw)
        ax.set_ylabel("Current")
        return fig, ax

    def plot_voltage(self, ax=None, x=None, **kw) -> tuple[Figure, Axes]:
        fig, ax = _make_ax(ax)
        x = x if x is not None else self._time
        if x is not None:
            ax.plot(x, self.voltage, **kw)
            ax.set_xlim(x[0], x[-1])
        else:
            ax.plot(self.voltage, **kw)
        ax.set_ylabel("Voltage")
        return fig, ax


@dataclass
class CircuitData:
    units: tuple[str, str, str]  # (current_unit, voltage_unit, flux_unit)
    sources: list[CircuitElement]
    power_sources: list[CircuitElement]


# ── Network ────────────────────────────────────────────────────────────────


@dataclass
class NetworkElement:
    element_num: int
    element_name: str
    current: np.ndarray
    voltage: np.ndarray
    flux: np.ndarray | None
    _time: np.ndarray | None = field(default=None, repr=False, compare=False, init=False)

    def plot_current(self, ax=None, x=None, **kw) -> tuple[Figure, Axes]:
        fig, ax = _make_ax(ax)
        x = x if x is not None else self._time
        label = kw.pop("label", f"{self.element_name} #{self.element_num}")
        if x is not None:
            ax.plot(x, self.current, label=label, **kw)
            ax.set_xlim(x[0], x[-1])
        else:
            ax.plot(self.current, label=label, **kw)
        ax.set_ylabel("Current")
        return fig, ax

    def plot_voltage(self, ax=None, x=None, **kw) -> tuple[Figure, Axes]:
        fig, ax = _make_ax(ax)
        x = x if x is not None else self._time
        label = kw.pop("label", f"{self.element_name} #{self.element_num}")
        if x is not None:
            ax.plot(x, self.voltage, label=label, **kw)
            ax.set_xlim(x[0], x[-1])
        else:
            ax.plot(self.voltage, label=label, **kw)
        ax.set_ylabel("Voltage")
        return fig, ax


@dataclass
class NetworkData:
    units: tuple[str, str, str]  # (current_unit, voltage_unit, flux_unit)
    elements: list[NetworkElement]


# ── Force nodal ────────────────────────────────────────────────────────────


@dataclass
class ForceNodalEntry:
    property_num: int
    force_x: np.ndarray
    force_y: np.ndarray
    force_z: np.ndarray
    force_mx: np.ndarray
    force_my: np.ndarray
    force_mz: np.ndarray
    _time: np.ndarray | None = field(default=None, repr=False, compare=False, init=False)


@dataclass
class ForceNodalData:
    units: tuple[str, str]  # (force_unit, moment_unit)
    entries: list[ForceNodalEntry]


@dataclass(frozen=True)
class PlotAxisOption:
    key: str
    label: str
    values: np.ndarray
    unit: str | None = None

    @property
    def axis_label(self) -> str:
        return _format_label_with_unit(self.label, self.unit)


@dataclass(frozen=True)
class PlotSeriesDescriptor:
    tree_path: tuple[str, ...]
    label: str
    values: np.ndarray
    quantity: str
    unit: str | None = None

    @property
    def axis_label(self) -> str:
        return _format_label_with_unit(self.quantity, self.unit)


# ── Top-level result ───────────────────────────────────────────────────────


def _format_label_with_unit(label: str, unit: str | None) -> str:
    if unit:
        return f"{label} ({unit})"
    return label


@dataclass
class EMSolutionOutput:
    meta: MetaData
    condition: AnalysisCondition
    time: np.ndarray
    time_unit: str
    position: np.ndarray | None
    position_unit: str | None
    motion_direction: str | None
    circuit: CircuitData | None
    network: NetworkData | None
    force_nodal: ForceNodalData | None

    @classmethod
    def from_dict(cls, d: dict) -> "EMSolutionOutput":
        meta_d = d["metaData"]
        meta = MetaData(
            version=meta_d["EMSolutionVersion"],
            release_date=meta_d["releaseDate"],
            creation_date=meta_d["creationDate"],
            comments=meta_d.get("comments", ""),
        )

        cond_d = d["analysisCondition"]
        condition = AnalysisCondition(
            analysis_type=cond_d["analysisType"],
            nonlinear=cond_d["nonlinear"],
            motion_type=cond_d["motionType"],
            circuit_type=cond_d["circuitType"],
        )

        ts = d["timeStep"]
        time = _arr(ts["time"])
        time_unit = ts.get("timeUnit", "s")

        raw_pos = ts.get("position")
        position = _arr(raw_pos[0]) if raw_pos else None
        position_unit = ts.get("positionUnit")
        motion_direction = ts.get("motionDirection")

        post = d.get("postData", {})

        # Circuit
        circuit: CircuitData | None = None
        if "circuit" in post:
            c = post["circuit"]
            units = tuple(c["circuitUnit"])

            def _circ_el(e: dict) -> CircuitElement:
                flux_raw = e.get("flux")
                return CircuitElement(
                    serial_num=int(e["serialNum"]),
                    current=_arr(e["current"]),
                    voltage=_arr(e["voltage"]),
                    flux=_arr(flux_raw) if flux_raw is not None else None,
                )

            circuit = CircuitData(
                units=units,
                sources=[_circ_el(e) for e in c.get("sourceData", [])],
                power_sources=[_circ_el(e) for e in c.get("powerSourceData", [])],
            )

        # Network
        network: NetworkData | None = None
        if "network" in post:
            n = post["network"]
            units = tuple(n["networkUnit"])

            def _net_el(e: dict) -> NetworkElement:
                flux_raw = e.get("flux")
                return NetworkElement(
                    element_num=int(e["elementNum"]),
                    element_name=str(e["elementName"]),
                    current=_arr(e["current"]),
                    voltage=_arr(e["voltage"]),
                    flux=_arr(flux_raw) if flux_raw is not None else None,
                )

            network = NetworkData(
                units=units,
                elements=[_net_el(e) for e in n.get("networkData", [])],
            )

        # Force nodal
        force_nodal: ForceNodalData | None = None
        if "forceNodal" in post:
            fn = post["forceNodal"]
            units = tuple(fn["forceUnit"])

            def _force_en(e: dict) -> ForceNodalEntry:
                return ForceNodalEntry(
                    property_num=e["propertyNum"],
                    force_x=_arr(e["forceX"]),
                    force_y=_arr(e["forceY"]),
                    force_z=_arr(e["forceZ"]),
                    force_mx=_arr(e["forceMX"]),
                    force_my=_arr(e["forceMY"]),
                    force_mz=_arr(e["forceMZ"]),
                )

            force_nodal = ForceNodalData(
                units=units,
                entries=[_force_en(e) for e in fn.get("forceNodalData", [])],
            )

        result = cls(
            meta=meta,
            condition=condition,
            time=time,
            time_unit=time_unit,
            position=position,
            position_unit=position_unit,
            motion_direction=motion_direction,
            circuit=circuit,
            network=network,
            force_nodal=force_nodal,
        )

        # Inject _time back-reference on every leaf element
        if result.circuit:
            for el in result.circuit.sources + result.circuit.power_sources:
                el._time = result.time
        if result.network:
            for el in result.network.elements:
                el._time = result.time
        if result.force_nodal:
            for en in result.force_nodal.entries:
                en._time = result.time

        return result

    @classmethod
    def from_file(cls, path: str | Path) -> "EMSolutionOutput":
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def get_plot_x_options(self) -> list[PlotAxisOption]:
        options = [PlotAxisOption(key="time", label="Time", values=self.time, unit=self.time_unit)]
        if self.position is not None:
            options.append(
                PlotAxisOption(key="position", label="Position", values=self.position, unit=self.position_unit)
            )
        return options

    def get_plot_x_option(self, key: str) -> PlotAxisOption:
        for option in self.get_plot_x_options():
            if option.key == key:
                return option
        raise KeyError(f"Unknown plot x-axis: {key}")

    def get_plot_series(self) -> list[PlotSeriesDescriptor]:
        series: list[PlotSeriesDescriptor] = []

        if self.circuit is not None:
            current_unit, voltage_unit, flux_unit = self.circuit.units
            circuit_groups = (
                ("Sources", self.circuit.sources, "Source"),
                ("Power Sources", self.circuit.power_sources, "Power Source"),
            )
            for group_label, elements, item_label in circuit_groups:
                for element in elements:
                    base_path = ("Circuit", group_label, f"{item_label} #{element.serial_num}")
                    series.append(
                        PlotSeriesDescriptor(
                            tree_path=base_path + ("Current",),
                            label=f"{item_label} #{element.serial_num} Current",
                            values=element.current,
                            quantity="Current",
                            unit=current_unit,
                        )
                    )
                    series.append(
                        PlotSeriesDescriptor(
                            tree_path=base_path + ("Voltage",),
                            label=f"{item_label} #{element.serial_num} Voltage",
                            values=element.voltage,
                            quantity="Voltage",
                            unit=voltage_unit,
                        )
                    )
                    if element.flux is not None:
                        series.append(
                            PlotSeriesDescriptor(
                                tree_path=base_path + ("Flux",),
                                label=f"{item_label} #{element.serial_num} Flux",
                                values=element.flux,
                                quantity="Flux",
                                unit=flux_unit,
                            )
                        )

        if self.network is not None:
            current_unit, voltage_unit, flux_unit = self.network.units
            for element in self.network.elements:
                element_path = ("Network", f"{element.element_name} #{element.element_num}")
                series.append(
                    PlotSeriesDescriptor(
                        tree_path=element_path + ("Current",),
                        label=f"{element.element_name} #{element.element_num} Current",
                        values=element.current,
                        quantity="Current",
                        unit=current_unit,
                    )
                )
                series.append(
                    PlotSeriesDescriptor(
                        tree_path=element_path + ("Voltage",),
                        label=f"{element.element_name} #{element.element_num} Voltage",
                        values=element.voltage,
                        quantity="Voltage",
                        unit=voltage_unit,
                    )
                )
                if element.flux is not None:
                    series.append(
                        PlotSeriesDescriptor(
                            tree_path=element_path + ("Flux",),
                            label=f"{element.element_name} #{element.element_num} Flux",
                            values=element.flux,
                            quantity="Flux",
                            unit=flux_unit,
                        )
                    )

        if self.force_nodal is not None:
            force_unit, moment_unit = self.force_nodal.units
            component_map = (
                ("Force X", "force_x", force_unit),
                ("Force Y", "force_y", force_unit),
                ("Force Z", "force_z", force_unit),
                ("Moment X", "force_mx", moment_unit),
                ("Moment Y", "force_my", moment_unit),
                ("Moment Z", "force_mz", moment_unit),
            )
            for entry in self.force_nodal.entries:
                entry_path = ("Force Nodal", f"Property #{entry.property_num}")
                for quantity, attr_name, unit in component_map:
                    series.append(
                        PlotSeriesDescriptor(
                            tree_path=entry_path + (quantity,),
                            label=f"Property #{entry.property_num} {quantity}",
                            values=getattr(entry, attr_name),
                            quantity=quantity,
                            unit=unit,
                        )
                    )

        return series

    # ── Aggregate plot helpers ─────────────────────────────────────────────

    def plot_network(
        self,
        quantity: Literal["current", "voltage"] = "current",
        elements: list[NetworkElement] | None = None,
        ax: Axes | None = None,
        x: np.ndarray | None = None,
    ) -> tuple[Figure, Axes]:
        """Plot current or voltage for network elements on a single axes."""
        if self.network is None:
            raise ValueError("No network data in this result.")
        targets = elements if elements is not None else self.network.elements
        fig, ax = _make_ax(ax)
        for el in targets:
            if quantity == "voltage":
                el.plot_voltage(ax=ax, x=x)
            else:
                el.plot_current(ax=ax, x=x)
        ax.legend()
        return fig, ax

    def plot_circuit(
        self,
        quantity: Literal["current", "voltage"] = "voltage",
        ax: Axes | None = None,
        x: np.ndarray | None = None,
    ) -> tuple[Figure, Axes]:
        """Plot current or voltage for all circuit elements on a single axes."""
        if self.circuit is None:
            raise ValueError("No circuit data in this result.")
        all_elements = self.circuit.sources + self.circuit.power_sources
        fig, ax = _make_ax(ax)
        for el in all_elements:
            label = f"source #{el.serial_num}"
            if quantity == "voltage":
                el.plot_voltage(ax=ax, label=label, x=x)
            else:
                el.plot_current(ax=ax, label=label, x=x)
        ax.legend()
        return fig, ax

    def plot_forces(
        self,
        property_num: int | None = None,
        components: tuple[Literal["x", "y", "z", "mx", "my", "mz"], ...] = ("x", "y"),
        ax: Axes | None = None,
        x: np.ndarray | None = None,
    ) -> tuple[Figure, Axes]:
        """Plot force components for force-nodal entries on a single axes."""
        if self.force_nodal is None:
            raise ValueError("No force nodal data in this result.")
        entries = self.force_nodal.entries
        if property_num is not None:
            entries = [e for e in entries if e.property_num == property_num]
        fig, ax = _make_ax(ax)
        _component_map = {
            "x": "force_x",
            "y": "force_y",
            "z": "force_z",
            "mx": "force_mx",
            "my": "force_my",
            "mz": "force_mz",
        }
        last_t = None
        for en in entries:
            t = x if x is not None else en._time
            if t is not None:
                last_t = t
            for comp in components:
                attr = _component_map.get(comp)
                if attr is None:
                    continue
                data = getattr(en, attr)
                if t is not None:
                    ax.plot(t, data, label=f"prop#{en.property_num} F{comp}")
                else:
                    ax.plot(data, label=f"prop#{en.property_num} F{comp}")
        if last_t is not None:
            ax.set_xlim(last_t[0], last_t[-1])
        ax.legend()
        return fig, ax
