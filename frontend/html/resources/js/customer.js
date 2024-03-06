async function customerCheck() {
    await fetch("http://localhost:8001/customer/me", {
        method: 'GET',
        credentials: "include"
    }).then(async response => {
        if (response.status === 403 || response.status === 401 || response.status === 404) {
            Swal.fire({
                title: 'Error!',
                text: 'Sorry, you do not have an access to this page. Please, login with your customer account',
                icon: 'error',
                confirmButtonText: 'OK'
            }).then(() => {
                window.location.href = 'http://localhost:3001/login';
            });
        } else if (response.status === 500) {
            Swal.fire({
                title: 'Server Error!',
                text: 'An error occurred on the server. Please try again later.',
                icon: 'error',
                confirmButtonText: 'OK'
            }).then(() => {
                window.location.href = 'http://localhost:3001/home';
            });
        }
    })
}

document.addEventListener('DOMContentLoaded', customerCheck);