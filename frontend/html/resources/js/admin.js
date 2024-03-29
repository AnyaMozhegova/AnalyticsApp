function adminCheck() {
    return new Promise((resolve, reject) => {
        fetch("http://localhost:8001/admin/me", {
            method: 'GET',
            credentials: "include"
        }).then(response => {
            if (response.status === 403 || response.status === 401 || response.status === 404) {
                Swal.fire({
                    title: 'Error!',
                    text: 'Sorry, you do not have access to this page. Please, login with your admin account',
                    icon: 'error',
                    confirmButtonText: 'OK'
                }).then(() => {
                    window.location.href = 'http://localhost:3001/login';
                });
                reject(new Error('Access Denied'));
            } else if (response.status === 500) {
                Swal.fire({
                    title: 'Server Error!',
                    text: 'An error occurred on the server. Please try again later.',
                    icon: 'error',
                    confirmButtonText: 'OK'
                }).then(() => {
                    window.location.href = 'http://localhost:3001/admin-home';
                });
                reject(new Error('Server Error'));
            } else {
                response.json().then(data => resolve(data));
            }
        }).catch(error => {
            reject(error);
        });
    });
}

window.admin = {
    get: adminCheck
}
