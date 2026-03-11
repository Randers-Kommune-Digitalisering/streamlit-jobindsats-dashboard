import streamlit as st
import plotly.graph_objects as go

from utils.inputs_db_connection import get_inputs_db


db = get_inputs_db()


def last_consecutive_years(years: list[int], max_years: int = 3) -> list[int]:
    if not years:
        return []
    ys = sorted(set(int(y) for y in years))
    out = [ys[-1]]
    while len(out) < max_years:
        nxt = out[-1] - 1
        if nxt in ys:
            out.append(nxt)
        else:
            break
    return out


def list_series():
    rows = db.execute_sql(
        """
        SELECT id, name
        FROM app_series
        ORDER BY name;
        """
    )
    return [{"id": int(r[0]), "name": r[1]} for r in rows] if rows else []


def list_years(series_id: int):
    rows = db.execute_sql(
        """
        SELECT DISTINCT year
        FROM (
            SELECT year
            FROM app_budget_entries
            WHERE series_id = %s

            UNION

            SELECT year
            FROM app_targets
            WHERE series_id = %s
        ) y
        ORDER BY year;
        """,
        (series_id, series_id),
    )
    return [int(r[0]) for r in rows] if rows else []


def get_latest_budget_for_year(series_id: int, year: int):
    rows = db.execute_sql(
        """
        SELECT month, value
        FROM (
            SELECT DISTINCT ON (month)
                month, value, entered_at
            FROM app_budget_entries
            WHERE series_id = %s AND year = %s
            ORDER BY month, entered_at DESC
        ) x
        ORDER BY month;
        """,
        (series_id, year),
    )
    return [{"month": int(r[0]), "value": float(r[1])} for r in rows] if rows else []


def get_latest_target_for_year(series_id: int, year: int):
    rows = db.execute_sql(
        """
        SELECT target_value
        FROM app_targets
        WHERE series_id = %s AND year = %s
        ORDER BY entered_at DESC
        LIMIT 1;
        """,
        (series_id, year),
    )
    if not rows:
        return None
    return float(rows[0][0])


def get_series_year(series_id: int, year: int):
    return {
        "budget": get_latest_budget_for_year(series_id, year),
        "target": get_latest_target_for_year(series_id, year),
    }


def show_test_graph():
    st.subheader("Budget /  mål graf")

    # 1) Series list
    series_list = list_series()
    if not series_list:
        st.info("ingen serie fundet.")
        return

    name_to_id = {s["name"]: s["id"] for s in series_list}
    series_name = st.selectbox("Series", options=list(name_to_id.keys()))
    series_id = name_to_id[series_name]

    # 2) Years for series
    years = list_years(series_id)
    if not years:
        st.info("ingen år fundet for denne serie (ingen budget/mål endnu).")
        return

    year = st.selectbox("år", options=years, index=len(years) - 1)

    years_to_show = last_consecutive_years(years, max_years=3)

    show_last = st.checkbox("Vis seneste 3 år", value=False)

    # default: show just the selected year
    selected_years = [int(year)]

    # if checked: show last consecutive years
    if show_last:
        selected_years = years_to_show

    month_names = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
        5: "Maj", 6: "Jun", 7: "Jul", 8: "Aug",
        9: "Sep", 10: "Okt", 11: "Nov", 12: "Dec",
    }
    month_order = list(range(1, 13))
    x_months = [month_names[m] for m in month_order]

    fig = go.Figure()
    fig.update_layout(
        title=f"Budget per måned — {series_name} ({', '.join(map(str, selected_years))})",
        xaxis_title="Måned",
        yaxis_title="Værdi",
    )

    for y in selected_years:
        data = get_series_year(series_id, int(y))
        budget = data["budget"]

        month_to_value = {int(p["month"]): float(p["value"]) for p in budget}
        y_values = [month_to_value.get(m, None) for m in month_order]

        if any(v is not None for v in y_values):
            fig.add_trace(go.Scatter(
                x=x_months,
                y=y_values,
                mode="lines+markers",
                name=str(y)
            ))
        else:
            st.info(f"Ingen budget for {y}.")

    # Only show target line for single-year view
    if len(selected_years) == 1:
        y = selected_years[0]
        target = get_latest_target_for_year(series_id, int(y))
        if target is not None:
            fig.add_hline(
                y=float(target),
                line_dash="dash",
                annotation_text=f"Target {y}: {float(target):.2f}",
                annotation_position="top left",
            )
        else:
            st.info(f"Ingen mål for {y}.")

    st.plotly_chart(fig, use_container_width=True)