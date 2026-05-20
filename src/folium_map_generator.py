from pathlib import Path
import json
import folium
from folium.plugins import HeatMap
import pandas as pd


REGION_COLORS = {
    "North": "#2563eb",
    "Central": "#16a34a",
    "South": "#dc2626",
}


def clean_generated_html(output_file: Path):
    html = output_file.read_text(encoding="utf-8")

    html = html.replace(
        "<html>",
        '<html lang="en">'
    )

    html = html.replace(
        "<head>",
        '<head>\n    <meta charset="UTF-8">\n    <title>BAM Arrear Interactive Map</title>'
    )

    html = html.replace(
        "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no",
        "width=device-width, initial-scale=1.0"
    )

    output_file.write_text(html, encoding="utf-8")


class FoliumMapGenerator:

    def create_map(
        self,
        df: pd.DataFrame,
        output_file: Path,
        dark_mode: bool = False,
    ):
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if df.empty:
            center_lat = 19.314962
            center_lon = 84.794090
        else:
            center_lat = df["latitude"].mean()
            center_lon = df["longitude"].mean()

        tile_layer = "CartoDB dark_matter" if dark_mode else "CartoDB positron"

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,
            tiles=tile_layer,
            control_scale=True,
        )

        if not df.empty:
            heat_data = []

            for _, row in df.iterrows():
                weight = max(float(row["arrear_amount"]) / 10000, 0.4)

                heat_data.append([
                    row["latitude"],
                    row["longitude"],
                    weight,
                ])

            HeatMap(
                heat_data,
                name="🔥 Arrear Heatmap",
                radius=42,
                blur=34,
                min_opacity=0.35,
                max_zoom=15,
                gradient={
                    0.20: "#2563eb",
                    0.40: "#06b6d4",
                    0.60: "#22c55e",
                    0.80: "#facc15",
                    1.00: "#ef4444",
                },
            ).add_to(m)

        point_layer = folium.FeatureGroup(
            name="📍 Customer Points Auto-Zoom",
            show=False,
        )

        search_data = {}

        for _, row in df.iterrows():
            color = REGION_COLORS.get(row["region"], "#64748b")

            due_date_text = (
                row["due_date"].strftime("%d-%m-%Y")
                if hasattr(row["due_date"], "strftime")
                else str(row["due_date"])
            )

            popup_html = f"""
            <div style="width:300px;font-family:'Segoe UI', Arial, sans-serif;">
                <div style="
                    background:linear-gradient(135deg,#2563eb,#9333ea);
                    color:white;
                    padding:12px;
                    font-weight:800;
                    font-size:16px;
                    border-radius:12px 12px 0 0;
                ">
                    ⚡ {row['point_name']}
                </div>

                <div style="padding:12px;background:#ffffff;">
                    <table style="width:100%;border-collapse:collapse;font-size:13px;">
                        <tr><td><b>📍 Region</b></td><td>{row['region']}</td></tr>
                        <tr><td><b>📌 Status</b></td><td>{row['status']}</td></tr>
                        <tr><td><b>📅 Due Date</b></td><td>{due_date_text}</td></tr>
                        <tr><td><b>⏳ Overdue</b></td><td>{int(row['overdue_days'])} days</td></tr>
                        <tr><td><b>💰 Arrear</b></td><td>₹{row['arrear_amount']:,.0f}</td></tr>
                        <tr><td><b>🌐 Latitude</b></td><td>{row['latitude']}</td></tr>
                        <tr><td><b>🌐 Longitude</b></td><td>{row['longitude']}</td></tr>
                    </table>
                </div>
            </div>
            """

            marker = folium.CircleMarker(
                location=[
                    row["latitude"],
                    row["longitude"],
                ],
                radius=4,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.75,
                weight=1,
                popup=folium.Popup(
                    popup_html,
                    max_width=340,
                ),
                tooltip=str(row["point_name"]),
            )

            marker.add_to(point_layer)

            key = str(row["point_name"]).strip().lower()

            search_data[key] = {
                "name": str(row["point_name"]),
                "lat": float(row["latitude"]),
                "lon": float(row["longitude"]),
                "html": popup_html,
            }

        point_layer.add_to(m)

        folium.LayerControl(
            collapsed=False,
        ).add_to(m)

        map_name = m.get_name()
        point_layer_name = point_layer.get_name()
        search_json = json.dumps(search_data)

        custom_js = f"""
        <script>
        window.addEventListener("load", function () {{

            const customerData = {search_json};

            const mapObj = window["{map_name}"];
            const pointLayer = window["{point_layer_name}"];

            if (!mapObj || !pointLayer) {{
                console.error("Map or point layer not found.");
                return;
            }}

            function updatePointVisibility() {{
                if (mapObj.getZoom() >= 15) {{
                    if (!mapObj.hasLayer(pointLayer)) {{
                        mapObj.addLayer(pointLayer);
                    }}
                }} else {{
                    if (mapObj.hasLayer(pointLayer)) {{
                        mapObj.removeLayer(pointLayer);
                    }}
                }}
            }}

            mapObj.on("zoomend", updatePointVisibility);
            updatePointVisibility();

            const SearchControl = L.Control.extend({{
                options: {{
                    position: "topright"
                }},

                onAdd: function () {{
                    const div = L.DomUtil.create("div", "custom-search-box");

                    div.innerHTML = `
                        <div style="
                            background:white;
                            padding:12px;
                            border-radius:16px;
                            box-shadow:0 6px 22px rgba(0,0,0,0.28);
                            font-family:Arial;
                            width:245px;
                        ">
                            <div style="
                                font-weight:900;
                                margin-bottom:8px;
                                color:#1e293b;
                            ">
                                🔎 Smart Search
                            </div>

                            <input
                                id="customerSearchInput"
                                type="text"
                                placeholder="Search acc_25"
                                style="
                                    width:100%;
                                    padding:9px;
                                    border:1px solid #cbd5e1;
                                    border-radius:999px;
                                    outline:none;
                                "
                            >

                            <button
                                id="customerSearchBtn"
                                type="button"
                                style="
                                    margin-top:8px;
                                    width:100%;
                                    padding:9px;
                                    border:none;
                                    border-radius:999px;
                                    background:linear-gradient(135deg,#2563eb,#9333ea);
                                    color:white;
                                    font-weight:900;
                                    cursor:pointer;
                                "
                            >
                                Go
                            </button>

                            <div
                                id="searchMsg"
                                style="
                                    margin-top:7px;
                                    font-size:12px;
                                    color:#dc2626;
                                    font-weight:800;
                                ">
                            </div>
                        </div>
                    `;

                    L.DomEvent.disableClickPropagation(div);
                    L.DomEvent.disableScrollPropagation(div);

                    return div;
                }}
            }});

            mapObj.addControl(new SearchControl());

            function performCustomerSearch() {{
                const inputEl = document.getElementById("customerSearchInput");
                const msg = document.getElementById("searchMsg");

                if (!inputEl || !msg) {{
                    return;
                }}

                const input = inputEl.value.trim().toLowerCase();

                if (!input) {{
                    msg.style.color = "#dc2626";
                    msg.innerText = "Enter acc_no";
                    return;
                }}

                if (!customerData[input]) {{
                    msg.style.color = "#dc2626";
                    msg.innerText = "Not found";
                    return;
                }}

                const item = customerData[input];

                mapObj.setView([item.lat, item.lon], 17);

                if (!mapObj.hasLayer(pointLayer)) {{
                    mapObj.addLayer(pointLayer);
                }}

                L.popup({{ maxWidth: 340 }})
                    .setLatLng([item.lat, item.lon])
                    .setContent(item.html)
                    .openOn(mapObj);

                msg.style.color = "#16a34a";
                msg.innerText = "Found " + item.name;
            }}

            setTimeout(function () {{
                const btn = document.getElementById("customerSearchBtn");
                const input = document.getElementById("customerSearchInput");

                if (btn) {{
                    btn.onclick = performCustomerSearch;
                }}

                if (input) {{
                    input.addEventListener("keydown", function(e) {{
                        if (e.key === "Enter") {{
                            performCustomerSearch();
                        }}
                    }});
                }}
            }}, 300);

        }});
        </script>
        """

        m.get_root().html.add_child(
            folium.Element(custom_js)
        )

        m.save(output_file)
        clean_generated_html(output_file)

        return output_file