document.body.addEventListener('htmx:afterOnLoad', function (event) {
    // Check if the response contains JSON content
    const contentType = event.detail.xhr.getResponseHeader("Content-Type");
    if (contentType && contentType.indexOf("application/json") !== -1) {
        // Parse the JSON response
        const response = JSON.parse(event.detail.xhr.responseText);
        if (response.id) {
            // Assuming the backend response contains an "id" field
            sessionStorage.setItem('userId', response.id);
        }
    }
});