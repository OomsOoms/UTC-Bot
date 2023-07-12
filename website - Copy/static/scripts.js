document.getElementById('query-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent form submission

    var queryInput = document.querySelector('input[name="query"]');
    var query = queryInput.value;

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/execute_query', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            console.log(response); // Do something with the JSON response
        }
    };

    xhr.send('query=' + encodeURIComponent(query));
});
