import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from fpdf import FPDF

CHART_OUTPUT_DIR = "generated_charts"

def create_line_chart(filtered_data):
    if not os.path.exists(CHART_OUTPUT_DIR):
        os.makedirs(CHART_OUTPUT_DIR)

    # 1) Daten parsen: {Datum_objekt: [Werte]}
    day_values = {}
    for row in filtered_data:
        d_str = row[0]  # z.B. "2025-01-01"
        try:
            d_obj = datetime.strptime(d_str, "%Y-%m-%d")
            val = int(row[2])
        except ValueError:
            continue
        day_values.setdefault(d_obj, []).append(val)

    # 2) Daten sortieren und tägliche Durchschnitte berechnen
    sorted_dates = sorted(day_values.keys())
    averages = [sum(day_values[d]) / len(day_values[d]) for d in sorted_dates]

    # 3) Plot erstellen
    plt.figure(figsize=(6, 4))
    plt.plot(sorted_dates, averages, marker='o', color="blue")
    plt.title("Daily Average Mood")
    plt.xlabel("Date")
    plt.ylabel("Average Mood")

    # 4) X-Achse konfigurieren (Datumsformatierung)
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=10))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
    plt.xticks(rotation=45, fontsize=8)

    # 5) Plot speichern
    out_path = os.path.join(CHART_OUTPUT_DIR, "line_chart.png")
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()

    return out_path

def create_daily_pie_charts(filtered_data):
    if not os.path.exists(CHART_OUTPUT_DIR):
        os.makedirs(CHART_OUTPUT_DIR)

    color_mapping = {
        6: "lightgreen", 5: "darkgreen",
        4: "lightsalmon", 3: "darkred",
        2: "lightgrey",   1: "darkgrey",
        0: "black"
    }

    unique_dates = sorted(set(row[0] for row in filtered_data))
    paths = []
    for d in unique_dates:
        day_data = [row for row in filtered_data if row[0] == d]
        frequency = {}
        for row in day_data:
            try:
                val = int(row[2])
            except ValueError:
                continue
            frequency[val] = frequency.get(val, 0) + 1

        labels, sizes, colors = [], [], []
        for val in sorted(frequency.keys(), reverse=True):
            labels.append(str(val))
            sizes.append(frequency[val])
            colors.append(color_mapping.get(val, "grey"))
        if not sizes:
            continue

        date_tag = d.replace("-", "")
        out_path = os.path.join(CHART_OUTPUT_DIR, f"pie_{date_tag}.png")

        plt.figure(figsize=(5, 3), facecolor="white")
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
        plt.title(f"Pie Chart for {d}")
        plt.savefig(out_path, bbox_inches='tight', facecolor="white")
        plt.close()
        paths.append(out_path)
    return paths

def create_bar_chart(filtered_data):
    if not os.path.exists(CHART_OUTPUT_DIR):
        os.makedirs(CHART_OUTPUT_DIR)
    frequency = {}
    for row in filtered_data:
        try:
            val = int(row[2])
        except ValueError:
            continue
        frequency[val] = frequency.get(val, 0) + 1
    keys = sorted(frequency.keys(), reverse=True)
    values = [frequency[k] for k in keys]
    color_mapping = {
        6: "lightgreen",
        5: "darkgreen",
        4: "lightsalmon",
        3: "darkred",
        2: "lightgrey",
        1: "darkgrey",
        0: "black"
    }
    colors = [color_mapping.get(k, "grey") for k in keys]
    plt.figure(figsize=(5, 3))
    plt.bar([str(k) for k in keys], values, color=colors)
    plt.title("Bar Chart Example")
    out_path = os.path.join(CHART_OUTPUT_DIR, "bar_chart.png")
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    return out_path

def create_summary_pie_chart(filtered_data):
    if not os.path.exists(CHART_OUTPUT_DIR):
        os.makedirs(CHART_OUTPUT_DIR)
    frequency = {}
    for row in filtered_data:
        try:
            val = int(row[2])
        except ValueError:
            continue
        frequency[val] = frequency.get(val, 0) + 1
    keys = sorted(frequency.keys(), reverse=True)
    sizes = [frequency[k] for k in keys]
    color_mapping = {
        6: "lightgreen",
        5: "darkgreen",
        4: "lightsalmon",
        3: "darkred",
        2: "lightgrey",
        1: "darkgrey",
        0: "black"
    }
    colors = [color_mapping.get(k, "grey") for k in keys]
    plt.figure(figsize=(5, 3))
    plt.pie(sizes, labels=[str(k) for k in keys], colors=colors, autopct='%1.1f%%')
    plt.title("Summary Pie Chart")
    out_path = os.path.join(CHART_OUTPUT_DIR, "summary_pie.png")
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    return out_path

def generate_pdf_from_images(image_paths, output_pdf):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    for img_path in image_paths:
        pdf.add_page()
        pdf.image(img_path, x=10, y=10, w=180)
    pdf.output(output_pdf, "F")

