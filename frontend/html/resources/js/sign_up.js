document.querySelectorAll('.input-field').forEach(input => {
    const tooltip = input.nextElementSibling.querySelector('.tooltiptext');
    if (tooltip) {
        input.addEventListener('focus', () => {
            tooltip.style.visibility = 'visible';
            tooltip.style.opacity = 1;
        });
        input.addEventListener('blur', () => {
            tooltip.style.visibility = 'hidden';
            tooltip.style.opacity = 0;
        });
    }
});
document.body.addEventListener('htmx:afterOnLoad', function (event) {
    const status = event.detail.xhr.status;
    const contentType = event.detail.xhr.getResponseHeader("Content-Type");

    if (contentType && contentType.indexOf("application/json") !== -1 && status === 201) {
        const response = JSON.parse(event.detail.xhr.responseText);
        if (response.id) {
            sessionStorage.setItem('userId', response.id);
            Swal.fire({
                title: 'Success!',
                text: 'Sign up is successful!',
                icon: 'success',
                confirmButtonText: 'OK'
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = 'http://0.0.0.0:3001/home';
                }
            });
        }
    } else if (status === 400) {
        Swal.fire({
            title: 'Error!',
            text: 'User data is incorrect. Make sure the fields are not empty and that password and password confirm match.',
            icon: 'error',
            confirmButtonText: 'OK'
        });
    } else if (status === 500) {
        Swal.fire({
            title: 'Server Error!',
            text: 'An error occurred on the server. Please try again later.',
            icon: 'error',
            confirmButtonText: 'OK'
        });
    }
});
