"""Shared colours and Altair chart builders.

Colours follow the validated reference palette (dataviz skill, references/palette.md):
categorical slots in fixed order; colour follows the entity, never its rank.
"""
import altair as alt
import pandas as pd

SLOTS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
MUTED = "#898781"

ORIGIN_ORDER = ["Mostly imported", "Locally processed / mixed", "Mostly local"]
ORIGIN_SCALE = alt.Scale(domain=ORIGIN_ORDER, range=SLOTS[:3])

STATUS_CRITICAL = "#d03b3b"


def _base(chart: alt.Chart, height: int = 320) -> alt.Chart:
    return chart.properties(height=height).configure_axis(grid=True, gridOpacity=0.35, domain=False, tickSize=0,
                                                         labelPadding=6).configure_view(stroke=None)


def lines(df: pd.DataFrame, x: str, y: str, series: str, colors: dict[str, str], y_title: str,
          log: bool = False, y_format: str = ",.0f", height: int = 320, x_title: str | None = None) -> alt.Chart:
    """Multi-series line chart with crosshair tooltip. `colors` pins each series to its slot."""
    domain = list(colors)
    scale = alt.Scale(domain=domain, range=[colors[d] for d in domain])
    nearest = alt.selection_point(nearest=True, on="pointerover", fields=[x], empty=False)
    base = alt.Chart(df).encode(
        x=alt.X(f"{x}:T", title=x_title),
        y=alt.Y(f"{y}:Q", title=y_title, scale=alt.Scale(type="log") if log else alt.Scale(zero=False),
                axis=alt.Axis(format=y_format)),
        color=alt.Color(f"{series}:N", scale=scale, legend=alt.Legend(orient="top", title=None, columns=2 if len(domain) > 2 else 0)),
    )
    line = base.mark_line(strokeWidth=2)
    points = base.mark_point(size=60, filled=True).encode(opacity=alt.condition(nearest, alt.value(1), alt.value(0)))
    present = [d for d in domain if d in set(df[series])]
    rule = alt.Chart(df).transform_pivot(series, value=y, groupby=[x]).mark_rule(color=MUTED, strokeWidth=1).encode(
        x=f"{x}:T", opacity=alt.condition(nearest, alt.value(0.6), alt.value(0)),
        tooltip=[alt.Tooltip(f"{x}:T", title="Month", format="%b %Y")]
                + [alt.Tooltip(field=d, type="quantitative", format=y_format) for d in present],
    ).add_params(nearest)
    return _base(alt.layer(line, points, rule), height)


def hbars(df: pd.DataFrame, value: str, label: str, value_title: str, color: str | None = None,
          color_field: str | None = None, color_scale: alt.Scale | None = None, value_format: str = ",.0f",
          sort: str = "-x", tooltip: list | None = None, height: int | None = None) -> alt.Chart:
    """Horizontal bar chart (labels read well on phones). One colour unless `color_field` is set."""
    enc = dict(
        x=alt.X(f"{value}:Q", title=value_title, axis=alt.Axis(format=value_format)),
        y=alt.Y(f"{label}:N", sort=sort, title=None, axis=alt.Axis(labelLimit=180, labelOverlap=False)),
        tooltip=tooltip or [alt.Tooltip(f"{label}:N"), alt.Tooltip(f"{value}:Q", format=value_format)],
    )
    if color_field:
        enc["color"] = alt.Color(f"{color_field}:N", scale=color_scale, legend=alt.Legend(orient="top", title=None, columns=2))
    chart = alt.Chart(df).mark_bar(cornerRadiusEnd=4, height={"band": 0.7}, color=color or SLOTS[0]).encode(**enc)
    return _base(chart, height or max(140, 30 * df[label].nunique()))


def vbars(df: pd.DataFrame, x: str, y: str, y_title: str, y_format: str = ",.0f", height: int = 260,
          x_type: str = "O") -> alt.Chart:
    chart = alt.Chart(df).mark_bar(cornerRadiusEnd=4, color=SLOTS[0]).encode(
        x=alt.X(f"{x}:{x_type}", title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y(f"{y}:Q", title=y_title, axis=alt.Axis(format=y_format)),
        tooltip=[alt.Tooltip(f"{x}:{x_type}"), alt.Tooltip(f"{y}:Q", format=y_format)],
    )
    return _base(chart, height)
