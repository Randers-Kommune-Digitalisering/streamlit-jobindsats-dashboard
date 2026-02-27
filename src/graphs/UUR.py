import streamlit as st
import plotly.graph_objects as go

from utils.input_api_client import list_series, list_years, get_series_year, get_input_api_url





def last_consecutive_years(years: list[int], max_years: int = 3) -> list[int]:
    if not years:
        return []
    ys = sorted(set(int(y) for y in years))
    out = [ys[-1]]  # latest
    while len(out) < max_years:
        nxt = out[-1] - 1
        if nxt in ys:
            out.append(nxt)
        else:
            break
    return out


def show_UUR_graph():
    st.subheader("Budget / Target graph")
    st.caption(f"API: {get_input_api_url()}")

    # 1) Series list
    series_list = list_series()
    if not series_list:
        st.info("No series found.")
        return

    name_to_id = {s["name"]: s["id"] for s in series_list}
    series_name = st.selectbox("Series", options=list(name_to_id.keys()))
    series_id = name_to_id[series_name]

    # 2) Years for series
    years = list_years(series_id)
    if not years:
        st.info("No years found for this series (no budget/targets yet).")
        return

    year = st.selectbox("Year", options=years, index=len(years) - 1)

    years_to_show = last_consecutive_years(years, max_years=3)

    show_last = st.checkbox("Vis seneste 3 år", value=False)

    # default: show just the selected year
    selected_years = [int(year)]

    # if checked: show last consecutive years (e.g. 2026, 2025, 2024)
    if show_last:
        selected_years = years_to_show

    # 3) Plot budget + target for one or multiple years
    fig = go.Figure()
    fig.update_layout(
        title=f"Budget per måned — {series_name} ({', '.join(map(str, selected_years))})"
    )

    for y in selected_years:
        data = get_series_year(series_id, int(y))
        budget = data["budget"]   # [{month, value}, ...]
        target = data["target"]   # float or None

        # Plot budget
        if budget:
            xs = [f"{y}-{int(p['month']):02d}" for p in budget]
            ys = [float(p["value"]) for p in budget]
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines+markers", name=f"Budget {y}"))
        else:
            st.info(f"Ingen budget for {y} (viser kun target hvis den findes).")

        # Plot target (optional)
        if target is not None:
            fig.add_hline(
                y=float(target),
                line_dash="dash",
                annotation_text=f"Target {y}: {float(target):.2f}",
                annotation_position="top left",
            )
        else:
            st.info(f"Ingen target for {y}.")

    st.plotly_chart(fig, use_container_width=True)