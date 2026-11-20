# ============================================================
# COMPLETE ERROR-FREE app.py
# COPY FULL CODE → REPLACE OLD app.py → SAVE → RUN
# ============================================================

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import mysql.connector

# ============================================================
# FLASK SETUP
# ============================================================
app = Flask(__name__)
CORS(app)

# ============================================================
# MYSQL DATABASE CONFIG
# ============================================================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root123",
    "database": "g5_gdp_recovery"
}

# ============================================================
# DATABASE CONNECTION FUNCTION
# ============================================================
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


# ============================================================
# FRONTEND ROUTES
# ============================================================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/data")
def data():
    return render_template("data.html")


@app.route("/analysis")
def analysis():
    return render_template("analysis.html")


@app.route("/insights")
def insights():
    return render_template("insights.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ============================================================
# INSIGHTS PAGE QUERIES (YOUR 9 QUERY SYSTEM)
# ============================================================
QUERIES = {
    "q1": {
        "title": "All Countries – GDP Growth Rate by Year",
        "sql": """
            SELECT country_name, year, gdp_growth_rate
            FROM gdp_growth
            ORDER BY country_name, year
        """
    },

    "q2": {
        "title": "COVID Impact Year (2020) – Worst Performers First",
        "sql": """
            SELECT country_name, gdp_growth_rate
            FROM gdp_growth
            WHERE year = 2020
            ORDER BY gdp_growth_rate ASC
        """
    },

    "q3": {
        "title": "Recovery Year (2021) – Best Rebound First",
        "sql": """
            SELECT country_name, gdp_growth_rate
            FROM gdp_growth
            WHERE year = 2021
            ORDER BY gdp_growth_rate DESC
        """
    },

    "q4": {
        "title": "All Countries – Inflation Rate by Year",
        "sql": """
            SELECT country_name, year, inflation_rate
            FROM inflation
            ORDER BY country_name, year
        """
    },

    "q5": {
        "title": "Post-Surge Year (2022) – Highest Inflation First",
        "sql": """
            SELECT country_name, inflation_rate
            FROM inflation
            WHERE year = 2022
            ORDER BY inflation_rate DESC
        """
    },

    "q6": {
        "title": "All Countries – Unemployment Rate by Year",
        "sql": """
            SELECT country_name, year, unemployment_rate
            FROM unemployment
            ORDER BY country_name, year
        """
    },

    "q7": {
        "title": "Latest Year (2024) – Lowest Unemployment First",
        "sql": """
            SELECT country_name, unemployment_rate
            FROM unemployment
            WHERE year = 2024
            ORDER BY unemployment_rate ASC
        """
    },

    "q8": {
        "title": "All Countries – GDP Value by Year",
        "sql": """
            SELECT country_name, year, gdp_value
            FROM gdp_value
            ORDER BY country_name, year
        """
    },

    "q9": {
        "title": "Latest Year (2024) – Largest Economy First",
        "sql": """
            SELECT country_name, gdp_value
            FROM gdp_value
            WHERE year = 2024
            ORDER BY gdp_value DESC
        """
    }
}


# ============================================================
# RUN QUERY API FOR INSIGHTS
# ============================================================
@app.route("/run_query/<query_id>")
def run_query(query_id):

    if query_id not in QUERIES:
        return jsonify({"error": "Query not found"}), 404

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(QUERIES[query_id]["sql"])

        rows = cursor.fetchall()

        columns = []
        for col in cursor.description:
            columns.append(col[0])

        cursor.close()
        conn.close()

        return jsonify({
            "title": QUERIES[query_id]["title"],
            "columns": columns,
            "rows": rows
        })

    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# DATA PAGE APIs
# ============================================================

# COUNTRY DROPDOWN
@app.route("/api/countries")
def get_countries():

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT DISTINCT country_name
            FROM g5_countries
            ORDER BY country_name
        """

        cursor.execute(query)

        countries = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return jsonify({
            "countries": countries
        })

    except mysql.connector.Error as e:
        return jsonify({
            "error": str(e)
        }), 500


# YEAR DROPDOWN
@app.route("/api/years")
def get_years():

    country = request.args.get("country")

    if not country:
        return jsonify({
            "error": "Country is required"
        }), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT DISTINCT year
            FROM (
                SELECT year FROM gdp_growth WHERE country_name = %s
                UNION
                SELECT year FROM inflation WHERE country_name = %s
                UNION
                SELECT year FROM unemployment WHERE country_name = %s
                UNION
                SELECT year FROM gdp_value WHERE country_name = %s
            ) AS years_data
            ORDER BY year
        """

        cursor.execute(query, (country, country, country, country))

        years = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return jsonify({
            "years": years
        })

    except mysql.connector.Error as e:
        return jsonify({
            "error": str(e)
        }), 500


# FILTERED DATA FETCH
@app.route("/api/data")
def get_filtered_data():

    country = request.args.get("country")
    year = request.args.get("year")
    metric = request.args.get("metric", "all")

    if not country:
        return jsonify({
            "error": "Country is required"
        }), 400

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        result = {}

        # GDP GROWTH
        if metric in ["all", "gdp_growth"]:

            query = """
                SELECT country_name, year, gdp_growth_rate
                FROM gdp_growth
                WHERE country_name = %s
            """

            params = [country]

            if year:
                query += " AND year = %s"
                params.append(year)

            query += " ORDER BY year"

            cursor.execute(query, tuple(params))
            result["gdp_growth"] = cursor.fetchall()

        # INFLATION
        if metric in ["all", "inflation"]:

            query = """
                SELECT country_name, year, inflation_rate
                FROM inflation
                WHERE country_name = %s
            """

            params = [country]

            if year:
                query += " AND year = %s"
                params.append(year)

            query += " ORDER BY year"

            cursor.execute(query, tuple(params))
            result["inflation"] = cursor.fetchall()

        # UNEMPLOYMENT
        if metric in ["all", "unemployment"]:

            query = """
                SELECT country_name, year, unemployment_rate
                FROM unemployment
                WHERE country_name = %s
            """

            params = [country]

            if year:
                query += " AND year = %s"
                params.append(year)

            query += " ORDER BY year"

            cursor.execute(query, tuple(params))
            result["unemployment"] = cursor.fetchall()

        # GDP VALUE
        if metric in ["all", "gdp_value"]:

            query = """
                SELECT country_name, year, gdp_value
                FROM gdp_value
                WHERE country_name = %s
            """

            params = [country]

            if year:
                query += " AND year = %s"
                params.append(year)

            query += " ORDER BY year"

            cursor.execute(query, tuple(params))
            result["gdp_value"] = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(result)

    except mysql.connector.Error as e:
        return jsonify({
            "error": str(e)
        }), 500

# ─────────────────────────────────────────────────────────────────
# ADD THESE ROUTES TO YOUR EXISTING app.py
# Place them alongside your existing @app.route definitions
# ─────────────────────────────────────────────────────────────────

# ── /api/countries  (used by both data.html and analysis.html) ───
@app.route("/api/countries")
def api_countries():
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT country_name FROM g5_countries ORDER BY country_name")
        rows   = [r[0] for r in cursor.fetchall()]
        cursor.close(); conn.close()
        return jsonify({"countries": rows})
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500


# ── /api/years  (used by data.html) ─────────────────────────────
@app.route("/api/years")
def api_years():
    country = request.args.get("country", "")
    if not country:
        return jsonify({"error": "country parameter required"}), 400
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        # Pull distinct years across all four tables for this country
        cursor.execute("""
            SELECT DISTINCT year FROM gdp_growth  WHERE country_name = %s
            UNION
            SELECT DISTINCT year FROM inflation   WHERE country_name = %s
            UNION
            SELECT DISTINCT year FROM unemployment WHERE country_name = %s
            UNION
            SELECT DISTINCT year FROM gdp_value   WHERE country_name = %s
            ORDER BY year
        """, (country, country, country, country))
        years = [r[0] for r in cursor.fetchall()]
        cursor.close(); conn.close()
        return jsonify({"years": years})
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500


# ── /api/data  (used by data.html) ──────────────────────────────
@app.route("/api/data")
def api_data():
    country = request.args.get("country", "")
    year    = request.args.get("year",    "")
    metric  = request.args.get("metric",  "all")
    if not country:
        return jsonify({"error": "country parameter required"}), 400

    where_y = "AND year = %s" if year else ""

    def query(sql, params):
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            cursor.close(); conn.close()
            return rows
        except mysql.connector.Error as e:
            return []

    result = {}
    base_params = (country, int(year)) if year else (country,)

    if metric in ("all", "gdp_growth"):
        result["gdp_growth"] = query(
            f"SELECT country_name, year, gdp_growth_rate FROM gdp_growth WHERE country_name=%s {where_y} ORDER BY year",
            base_params)

    if metric in ("all", "inflation"):
        result["inflation"] = query(
            f"SELECT country_name, year, inflation_rate FROM inflation WHERE country_name=%s {where_y} ORDER BY year",
            base_params)

    if metric in ("all", "unemployment"):
        result["unemployment"] = query(
            f"SELECT country_name, year, unemployment_rate FROM unemployment WHERE country_name=%s {where_y} ORDER BY year",
            base_params)

    if metric in ("all", "gdp_value"):
        result["gdp_value"] = query(
            f"SELECT country_name, year, gdp_value FROM gdp_value WHERE country_name=%s {where_y} ORDER BY year",
            base_params)

    return jsonify(result)


# ── /api/recovery_years  (used by analysis.html) ─────────────────
@app.route("/api/recovery_years")
def api_recovery_years():
    country = request.args.get("country", "")
    if not country:
        return jsonify({"error": "country parameter required"}), 400
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT year FROM recovery_score WHERE country_name = %s ORDER BY year",
            (country,)
        )
        years = [r[0] for r in cursor.fetchall()]
        cursor.close(); conn.close()
        return jsonify({"years": years})
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500


# ── /api/recovery_score  (used by analysis.html) ─────────────────
@app.route("/api/recovery_score")
def api_recovery_score():
    country = request.args.get("country", "")
    year    = request.args.get("year",    "")
    if not country:
        return jsonify({"error": "country parameter required"}), 400

    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Columns in recovery_score table:
        #   country_name, year, gdp_growth, inflation_rate, unemployment_rate, recovery_score

        if year:
            cursor.execute("""
                SELECT country_name, year,
                       gdp_growth,
                       inflation_rate,
                       unemployment_rate,
                       recovery_score
                FROM recovery_score
                WHERE country_name = %s AND year = %s
                ORDER BY year
            """, (country, int(year)))
        else:
            cursor.execute("""
                SELECT country_name, year,
                       gdp_growth,
                       inflation_rate,
                       unemployment_rate,
                       recovery_score
                FROM recovery_score
                WHERE country_name = %s
                ORDER BY year
            """, (country,))

        rows = cursor.fetchall()
        cursor.close(); conn.close()
        return jsonify({"rows": rows})
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500
    # ── /api/chart_data  (used by dashboard.html) ────────────────────
# Returns { rows: [ {year, value}, ... ] } for a country + metric.
# Metric values and their source tables / columns:
#
#   gdp_growth     → gdp_growth      table, column gdp_growth_rate
#   inflation      → inflation       table, column inflation_rate
#   unemployment   → unemployment    table, column unemployment_rate
#   gdp_value      → gdp_value       table, column gdp_value
#   recovery_score → recovery_score  VIEW,  column recovery_score
 
@app.route("/api/chart_data")
def api_chart_data():
    country = request.args.get("country", "")
    metric  = request.args.get("metric",  "")
 
    if not country or not metric:
        return jsonify({"error": "country and metric parameters are required"}), 400
 
    # Map metric key → (table/view name, value column)
    METRIC_MAP = {
        "gdp_growth":     ("gdp_growth",     "gdp_growth_rate"),
        "inflation":      ("inflation",       "inflation_rate"),
        "unemployment":   ("unemployment",    "unemployment_rate"),
        "gdp_value":      ("gdp_value",       "gdp_value"),
        "recovery_score": ("recovery_score",  "recovery_score"),
    }
 
    if metric not in METRIC_MAP:
        return jsonify({"error": f"Unknown metric '{metric}'"}), 400
 
    table, col = METRIC_MAP[metric]
 
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            f"SELECT year, {col} AS value FROM {table} "
            f"WHERE country_name = %s ORDER BY year",
            (country,)
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"rows": rows})
 
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500
 
# ============================================================
# RUN FLASK SERVER
# ============================================================
if __name__ == "__main__":
    app.run(debug=True)