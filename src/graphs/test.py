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


def show_test_graph():
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

    # 3) Plot budget + target for one or multiple years (overlay by month)
    month_names = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
        5: "Maj", 6: "Jun", 7: "Jul", 8: "Aug",
        9: "Sep", 10: "Okt", 11: "Nov", 12: "Dec",
    }
    month_order = list(range(1, 13))
    x_months = [month_names[m] for m in month_order]

    fig = go.Figure()
    fig.update_layout(
        title=f"Budget per måned — {series_name} ({', '.join(map(str, selected_years))})"
    )

    for y in selected_years:
        data = get_series_year(series_id, int(y))
        budget = data["budget"]   # [{month, value}, ...]
        target = data["target"]   # float or None

        # month -> value (sparse is fine)
        month_to_value = {int(p["month"]): float(p["value"]) for p in budget}

        # align values to Jan..Dec (None = missing month)
        y_values = [month_to_value.get(m, None) for m in month_order]

        # Budget line for that year
        if any(v is not None for v in y_values):
            fig.add_trace(go.Scatter(
                x=x_months,
                y=y_values,
                mode="lines+markers",
                name=str(y)   # legend shows just the year
            ))
        else:
            st.info(f"Ingen budget for {y}.")

    # Optional: only show target line when viewing a single year (avoids clutter)
    if len(selected_years) == 1:
        y = selected_years[0]
        data = get_series_year(series_id, int(y))
        target = data["target"]
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