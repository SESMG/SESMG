import pandas as pd
import altair as alt

def build_pareto_chart(additional_points: pd.DataFrame, mode: str) -> alt.Chart:
    if mode == "simplified":
        pareto_points = pd.DataFrame({
            "Costs in million Euro/a": [
                13.895, 
                12.560, 
                11.918, 
                11.349, 
                10.872,
                10.480, 
                10.124, 
                9.811, 
                9.596, 
                9.456,
                9.327, 
                9.198, 
                9.069, 
                8.940, 
                8.811,
                8.688, 
                8.587, 
                8.507, 
                8.442, 
                8.393,
                8.355, 
                8.329
            ],
            "CO2-emissions in t/a": [
                8210, 
                8300, 
                8362, 
                8513, 
                8664,
                8815, 
                8966, 
                9116, 
                9267, 
                9418,
                9569, 
                9720, 
                9871, 
                10022, 
                10173,
                10323, 
                10474, 
                10625, 
                10776, 
                10927,
                11078, 
                11229
            ]
        })
    elif mode == "advanced":
        pareto_points = pd.DataFrame({
            "Costs in million Euro/a": [
                13.895, 
                13.217, 
                11.995, 
                10.745, 
                10.251,
                9.822, 
                9.575, 
                9.413, 
                9.251, 
                9.089,
                8.927, 
                8.836, 
                8.793
            ],
            "CO2-emissions in t/a": [
                8210, 
                8356, 
                8840, 
                9500, 
                9766,
                10055, 
                10245, 
                10384, 
                10523, 
                10712,
                10902, 
                11091, 
                11280
            ]
        })
    else:
        pareto_points = pd.DataFrame()

    # Status quo
    status_quo = pd.DataFrame({
        "Costs in million Euro/a": [13.68616781],
        "CO2-emissions in t/a": [17221.43690357],
        "Name": ["Status Quo"]
    })

    # Combine with additional points if available
    combined_df = pd.concat([additional_points, status_quo], ignore_index=True)

    # Creating the graphics
    pareto_line = alt.Chart(pareto_points).mark_line().encode(
        x=alt.X("Costs in million Euro/a", 
                scale=alt.Scale(domain=(8.2, combined_df["Costs in million Euro/a"].max() * 1.05))),
        y=alt.Y("CO2-emissions in t/a", 
                scale=alt.Scale(domain=(8000, combined_df["CO2-emissions in t/a"].max() * 1.05)))
    )

    status_quo_label = alt.Chart(status_quo).mark_text(
        size=15, text="🔵 Status Quo", dx=40, dy=0, align="center", color="blue"
    ).encode(
        x="Costs in million Euro/a",
        y="CO2-emissions in t/a",
        tooltip=["Costs in million Euro/a", "CO2-emissions in t/a", "Name"]
    )

    additional_points_layer = alt.Chart(additional_points).mark_circle().encode(
        x="Costs in million Euro/a",
        y="CO2-emissions in t/a",
        color="Name"
    )

    return (pareto_line + status_quo_label + additional_points_layer).properties(width=1000, height=800).interactive()
