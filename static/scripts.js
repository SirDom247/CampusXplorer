// This function is called when the user initiates a search
function performSearch() {
    // Get the search term from the input field with the id 'search-bar'
    var searchTerm = document.getElementById('search-bar').value;

    // Make an AJAX request to the Flask backend for search
    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ search_term: searchTerm }),
    })
    .then(response => response.json())  // Parse the response as JSON
    .then(data => {
        // Update the search results on the front end
        displaySearchResults(data.results);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function displaySearchResults(results) {
    console.log('Results:', results);

    // Example: Render the results in a list
    var resultsContainer = document.getElementById('search-results');
    if (results && results.length > 0) {
        var resultListHTML = '<ul>';
        results.forEach(result => {
            // Display the state
            resultListHTML = '<h2>'+ result.state +'</h2>' + '<ul>';

            // Display all institutions in the specified state
            result.institutions.forEach(institution => {
                resultListHTML += '<li>' + institution.name + ' - ' + institution.ownership +'</li>';
            });

            // Close the inner ul tag for institutions
            resultListHTML += '</ul>';
        });

        resultsContainer.innerHTML = resultListHTML;
    } else {
        resultsContainer.innerHTML = '<p>No results found.</p>';
    }
}
