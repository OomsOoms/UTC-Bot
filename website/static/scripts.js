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

const editButtons = document.getElementsByClassName('edit-button');
for (let button of editButtons) {
    button.addEventListener('click', handleEditButtonClick);
}

function handleEditButtonClick(event) {
    const row = event.target.closest('tr');
    const rows = document.getElementsByTagName('tr');

    // Check if the row is already in edit mode
    const isEditMode = row.classList.contains('edit-mode');

    // Exit edit mode for other rows
    for (let i = 0; i < rows.length; i++) {
        const otherRow = rows[i];
        if (otherRow !== row && otherRow.classList.contains('edit-mode')) {
            exitEditMode(otherRow);
        }
    }

    if (isEditMode) {
        // If in edit mode, revert to normal view
        exitEditMode(row);
    } else {
        // If not in edit mode, enter edit mode
        row.classList.add('edit-mode');

        const cells = row.querySelectorAll('td');
        for (let i = 2; i < cells.length - 1; i++) { // Exclude first and last columns
            const cell = cells[i];
            const value = cell.innerText;
            cell.innerHTML = `<input type="text" value="${value}" />`;
        }

        // Update edit button and delete button
        const saveButton = row.querySelector('.edit-button');
        const cancelButton = row.querySelector('.delete-button');
        saveButton.innerText = 'Save';
        saveButton.style.backgroundColor = '#00c800';
        cancelButton.innerText = 'Cancel';
    }
}

function exitEditMode(row) {
    row.classList.remove('edit-mode');
    const cells = row.querySelectorAll('td');
    for (let i = 2; i < cells.length - 1; i++) { // Exclude first and last columns
        const cell = cells[i];
        const input = cell.querySelector('input');
        cell.innerText = input.value;
    }

    // Update edit button and delete button
    const saveButton = row.querySelector('.edit-button');
    const cancelButton = row.querySelector('.delete-button');
    saveButton.innerText = 'Edit';
    saveButton.style.backgroundColor = '';
    cancelButton.innerText = 'Delete';
}