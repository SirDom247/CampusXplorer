function performSearch() {
    var searchTerm = document.getElementById('search-bar').value;

    // Make an AJAX request to the Flask backend for search
    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ search_term: searchTerm }),
    })
    .then(response => response.json())
    .then(data => {
        // Update the search results on the front end
        displaySearchResults(data.results);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function displaySearchResults(results) {
    // Handle the search results, update the DOM, or perform other actions
    console.log(results);
    // Example: Render the results in a list
    var resultsContainer = document.getElementById('search-results');
    resultsContainer.innerHTML = '<ul>' + results.map(result => '<li>' + result.state + ' - ' + result.institutions[0].name + '</li>').join('') + '</ul>';
}
