from pathlib import Path
import io
import csv
import pandas as pd

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    session,
)

from werkzeug.security import generate_password_hash, check_password_hash

from src.data_processor import DataProcessor
from src.folium_map_generator import FoliumMapGenerator
from src.report_generator import ReportGenerator


app = Flask(__name__)

app.secret_key = "change-this-secret-key-before-deployment"


USERS = {
    "TPSODL": generate_password_hash("TPSODL123"),
    "NIRUPAMA": generate_password_hash("NIRUPAMA123"),
    "SUMA": generate_password_hash("SUMA123"),
    "SIVAKUMAR": generate_password_hash("SIVAKUMAR123"),
}


UPLOAD_FOLDER = Path("uploads_private")
OUTPUT_REPORT_FOLDER = Path("output_private/reports")
STATIC_FOLDER = Path("static")

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_REPORT_FOLDER.mkdir(parents=True, exist_ok=True)
STATIC_FOLDER.mkdir(parents=True, exist_ok=True)

DATA_FILE = UPLOAD_FOLDER / "manual_coordinates.csv"
MAP_FILE = STATIC_FOLDER / "generated_map.html"
REPORT_FILE = OUTPUT_REPORT_FOLDER / "arrear_summary.csv"


REQUIRED_COLUMNS = [
    "point_name",
    "latitude",
    "longitude",
    "due_date",
    "arrear_amount",
    "status",
]


def is_logged_in():
    return session.get("logged_in") is True


def clean_uploaded_csv(uploaded_file):
    content = uploaded_file.read()

    if not content.strip():
        raise ValueError("Uploaded CSV is empty.")

    text = content.decode("utf-8-sig", errors="replace")

    try:
        sample = text[:2048]
        dialect = csv.Sniffer().sniff(sample)
        delimiter = dialect.delimiter
    except Exception:
        delimiter = ","

    df = pd.read_csv(
        io.StringIO(text),
        sep=delimiter,
        engine="python",
        on_bad_lines="skip",
    )

    df.columns = df.columns.str.strip().str.lower()

    missing = set(REQUIRED_COLUMNS) - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}. "
            f"Required columns are: {REQUIRED_COLUMNS}"
        )

    df = df[REQUIRED_COLUMNS]

    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["arrear_amount"] = pd.to_numeric(
        df["arrear_amount"],
        errors="coerce",
    ).fillna(0)

    df["due_date"] = pd.to_datetime(
        df["due_date"],
        dayfirst=True,
        errors="coerce",
    )

    df["point_name"] = df["point_name"].astype(str).str.strip()
    df["status"] = df["status"].astype(str).str.strip().str.title()

    df = df.dropna(subset=["latitude", "longitude", "due_date"])

    if df.empty:
        raise ValueError("No valid coordinate rows found after cleaning CSV.")

    df.to_csv(DATA_FILE, index=False)


@app.route("/")
def home():
    if is_logged_in():
        return redirect(url_for("tpsodl_arrear_filter"))

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    message = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username in USERS and check_password_hash(USERS[username], password):
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("tpsodl_arrear_filter"))

        message = "Invalid username or password."

    return render_template("login.html", message=message)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/tpsodl_arrear_filter", methods=["GET", "POST"])
def tpsodl_arrear_filter():
    if not is_logged_in():
        return redirect(url_for("login"))

    message = None

    if request.method == "POST":
        uploaded_file = request.files.get("csv_file")

        if not uploaded_file or uploaded_file.filename == "":
            message = "Please choose a CSV file before uploading."
            return render_template("index.html", message=message)

        if not uploaded_file.filename.lower().endswith(".csv"):
            message = "Please upload only a .csv file."
            return render_template("index.html", message=message)

        try:
            clean_uploaded_csv(uploaded_file)
            message = "CSV uploaded and cleaned successfully."
        except Exception as e:
            message = f"Upload error: {e}"
            return render_template("index.html", message=message)

    if not DATA_FILE.exists():
        return render_template("index.html", message=message)

    try:
        processor = DataProcessor()
        df = processor.load_and_process(DATA_FILE)

        region = request.args.get("region", "All")
        timeline = request.args.get("timeline", "All")
        arrear = request.args.get("arrear", "All")
        status = request.args.get("status", "All")
        theme = request.args.get("theme", "light")

        filtered_df = processor.apply_filters(
            df,
            region=region,
            timeline=timeline,
            arrear=arrear,
            status=status,
        )

        dark_mode = theme == "dark"

        FoliumMapGenerator().create_map(
            filtered_df,
            MAP_FILE,
            dark_mode=dark_mode,
        )

        summary = ReportGenerator().generate_summary(
            filtered_df,
            REPORT_FILE,
        )

        stats = {
            "total_customers": len(filtered_df),
            "pending_customers": int((filtered_df["status"] == "Pending").sum()) if not filtered_df.empty else 0,
            "completed_customers": int((filtered_df["status"] == "Completed").sum()) if not filtered_df.empty else 0,
            "total_arrear": float(filtered_df["arrear_amount"].sum()) if not filtered_df.empty else 0,
        }

        return render_template(
            "tpsodl_arrear_filter.html",
            message=message,
            region=region,
            timeline=timeline,
            arrear=arrear,
            status=status,
            theme=theme,
            stats=stats,
            summary=summary.to_dict(orient="records"),
            username=session.get("username"),
        )

    except Exception as e:
        message = f"Processing error: {e}"
        return render_template("index.html", message=message)


@app.route("/map")
def map_view():
    if not is_logged_in():
        return redirect(url_for("login"))

    return render_template("map.html")


@app.route("/download_report")
def download_report():
    if not is_logged_in():
        return redirect(url_for("login"))

    if not REPORT_FILE.exists():
        return "Report not found. Please upload and process CSV first."

    return send_file(REPORT_FILE, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)