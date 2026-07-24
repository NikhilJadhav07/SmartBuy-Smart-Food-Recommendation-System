document.getElementById('search-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('food-input').value.trim();
    if (!input) return;

    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Finding recommendations...</div>';

    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `food_name=${encodeURIComponent(input)}`
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Response Data:", data);  // Debugging
        resultsDiv.innerHTML = '';

        if (!data.recommendations || data.recommendations.length === 0) {
            resultsDiv.innerHTML = '<p class="no-results">🍴 No recommendations found. Try another dish!</p>';
            return;
        }

        // Display Ingredients
        const ingredientsCard = document.createElement('div');
        ingredientsCard.className = 'food-card';
        ingredientsCard.innerHTML = `
            <h3>Ingredients for ${input}</h3>
            <p><strong>${data.ingredients}</strong></p>
        `;
        resultsDiv.appendChild(ingredientsCard);

        // Display Recommended Dishes
        data.recommendations.forEach(food => {
            const card = document.createElement('div');
            card.className = 'food-card';
            card.innerHTML = `
                <h3>${food}</h3>
            `;
            resultsDiv.appendChild(card);
        });

    } catch (error) {
        console.error('Error fetching recommendations:', error);
        resultsDiv.innerHTML = `<p class="error">⚠️ Error fetching recommendations: ${error.message}</p>`;
    }
});
