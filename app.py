from flask import Flask, render_template, request, jsonify
import mysql.connector
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random

app = Flask(__name__)

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shashi@932004",
        database="imdb_project"
    )

@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get dropdown values
    cursor.execute("SELECT DISTINCT genres FROM imdb_combined WHERE genres IS NOT NULL")
    genres = sorted(set(g[0] for g in cursor.fetchall() if g[0]))

    cursor.execute("SELECT DISTINCT language FROM imdb_combined WHERE language IS NOT NULL")
    languages = sorted(set(l[0] for l in cursor.fetchall() if l[0]))

    movies = []

    # Check for query parameters (GET)
    selected_genre = request.args.get("genre")
    selected_language = request.args.get("language")
    start_year = request.args.get("start_year")
    end_year = request.args.get("end_year")
    runtime = request.args.get("runtime")

    # Check for form data (POST)
    if request.method == "POST":
        selected_genre = request.form.get("genre")
        selected_language = request.form.get("language")
        start_year = request.form.get("start_year")
        end_year = request.form.get("end_year")
        runtime = request.form.get("runtime")

    # Construct query only if filters exist
    if any([selected_genre, selected_language, start_year, end_year, runtime]):
        query = """
            SELECT primaryTitle, originalTitle, language, startYear, runtimeMinutes, genres, averageRating, numVotes
            FROM imdb_combined WHERE 1=1
        """
        filters = []

        if selected_genre and selected_genre != "All":
            query += " AND genres LIKE %s"
            filters.append(f"%{selected_genre}%")

        if selected_language and selected_language != "All":
            query += " AND language = %s"
            filters.append(selected_language)

        if start_year:
            query += " AND startYear >= %s"
            filters.append(start_year)

        if end_year:
            query += " AND startYear <= %s"
            filters.append(end_year)

        if runtime:
            query += " AND runtimeMinutes >= %s"
            filters.append(runtime)

        query += " ORDER BY averageRating DESC LIMIT 25"
        cursor.execute(query, tuple(filters))
        movies = cursor.fetchall()

    conn.close()

    return render_template("index.html", genres=genres, languages=languages, movies=movies, filtered=any([selected_genre, selected_language, start_year, end_year, runtime]))

@app.route("/surprise_me", methods=["GET"])
def surprise_me():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT primaryTitle, originalTitle, language, startYear, runtimeMinutes, genres, averageRating, numVotes
        FROM imdb_combined WHERE primaryTitle IS NOT NULL AND language IS NOT NULL
        ORDER BY RAND() LIMIT 1
    """)
    movie = cursor.fetchone()

    conn.close()

    if movie:
        return jsonify({
            "primaryTitle": movie[0],
            "originalTitle": movie[1],
            "language": movie[2],
            "startYear": movie[3],
            "runtimeMinutes": movie[4],
            "genres": movie[5],
            "averageRating": movie[6],
            "numVotes": movie[7]
        })
    else:
        return jsonify({"error": "No movie found"})

import random

@app.route('/nlp_recommend', methods=['POST'])
def nlp_recommend():
    data = request.get_json()
    user_input = data.get('input_text') or data.get('nlp_input')  # handle both input names

    if not user_input:
        return jsonify({'error': 'No input provided.'})

    # Establish DB connection first
    conn = get_db_connection()
    cursor = conn.cursor()

    # Dummy query for now – you should replace with real NLP-based similarity results
    cursor.execute("SELECT primaryTitle, startYear, genres FROM imdb_combined WHERE primaryTitle IS NOT NULL AND genres IS NOT NULL LIMIT 50")
    rows = cursor.fetchall()

    # Add dummy similarity scores (in real implementation, you'd calculate these)
    results = [
        {
            'primaryTitle': row[0],
            'startYear': row[1],
            'genres': row[2],
            'similarity': round(random.uniform(0.7, 0.99), 2)  # simulate a similarity score
        } for row in rows
    ]

    # Sort by similarity, shuffle top results for variation
    results = sorted(results, key=lambda x: x['similarity'], reverse=True)[:20]
    random.shuffle(results)
    final_results = results[:5]

    return jsonify(final_results)

if __name__ == "__main__":
    app.run(debug=True)