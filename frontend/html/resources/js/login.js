document.body.addEventListener('htmx:afterOnLoad', function (event) {
    const status = event.detail.xhr.status;
    const contentType = event.detail.xhr.getResponseHeader("Content-Type");

    if (contentType && contentType.indexOf("application/json") !== -1 && status === 200) {
        const response = JSON.parse(event.detail.xhr.responseText);
        if (response.id) {
            sessionStorage.setItem('userId', response.id);
            Swal.fire({
                title: 'Success!',
                text: 'Login is successful!',
                icon: 'success',
                confirmButtonText: 'OK'
            }).then((result) => {
                if (result.isConfirmed) {
                    if (response.role === "customer")  window.location.href = 'http://localhost:3001/home';
                    else if (response.role === "admin") window.location.href = 'http://localhost:3001/admin_home';
                }
            });
        }
    } else if (status === 400) {
        Swal.fire({
            title: 'Error!',
            text: 'User data is incorrect. Make sure the fields are not empty and your account exists',
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