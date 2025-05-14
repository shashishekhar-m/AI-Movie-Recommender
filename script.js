let currentPage = 1;

document.addEventListener("DOMContentLoaded", () => {
    const showMoreBtn = document.getElementById("show-more-btn");
    if (showMoreBtn) {
        showMoreBtn.addEventListener("click", () => {
            currentPage++;
            fetch(`/recommend?page=${currentPage}`)
                .then(response => response.text())
                .then(html => {
                    const parser = new DOMParser();
                    const newCards = parser.parseFromString(html, 'text/html')
                                      .querySelector('.results').innerHTML;
                    document.querySelector('.results').innerHTML += newCards;
                })
                .catch(error => console.error('Error:', error));
        });
    }

    // Surprise Me Button
    const surpriseBtn = document.getElementById("surpriseMeBtn");
    if (surpriseBtn) {
        surpriseBtn.addEventListener("click", async function () {
            try {
                const response = await fetch("/surprise_me");
                const movie = await response.json();

                const results = document.getElementById("results");
                results.innerHTML = createMovieBox(movie); // Display one random movie
            } catch (error) {
                console.error("Surprise Me Error:", error);
            }
        });
    }

    // NLP Recommendation Button
    const nlpBtn = document.getElementById("nlpBtn");
    if (nlpBtn) {
        nlpBtn.addEventListener("click", async function () {
            const userInput = document.getElementById("nlpInput").value.trim();

            if (!userInput) {
                alert("Please describe your taste first!");
                return;
            }

            try {
                const response = await fetch("/nlp_recommend", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    body: `nlp_input=${encodeURIComponent(userInput)}`
                });

                const html = await response.text();

                const nlpResults = document.getElementById("nlpResults");
                nlpResults.innerHTML = html;
            } catch (error) {
                console.error("NLP Recommendation Error:", error);
            }
        });
    }
});

// Helper function to create a movie card for Surprise Me
function createMovieBox(movie) {
    return `
        <div class="movie-box">
            <h3>${movie.primaryTitle}</h3>
            <p><strong>Genres:</strong> ${movie.genres || 'N/A'}</p>
            ${movie.plot ? `<p>${movie.plot}</p>` : ""}
        </div>
    `;
}
