async function login() {
    const email = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const loginUrl = "http://localhost:8001/login";

    // Make the first POST request
    await fetch(loginUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            username: email,
            password: password
        },),
        credentials: "include"
    })
        .then(async response => {
                if (response.status === 401 || response.status === 400) {
                    Swal.fire({
                        title: 'Error!',
                        text: 'Incorrect email or password. Verify your input data',
                        icon: 'error',
                        confirmButtonText: 'OK'
                    })
                } else if (response.status === 500) {
                    Swal.fire({
                        title: 'Server Error!',
                        text: 'An error occurred on the server. Please try again later.',
                        icon: 'error',
                        confirmButtonText: 'OK'
                    });
                } else return await response.json()
            }
        )
        .then(async response => {
            sessionStorage.setItem('userId', response.id);
            Swal.fire({
                title: 'Success!',
                text: 'Login is successful!',
                icon: 'success',
                confirmButtonText: 'OK'
            }).then((result) => {
                if (result.isConfirmed) {
                    if (response.role === "customer") window.location.href = 'http://localhost:3001/home';
                    else if (response.role === "admin") window.location.href = 'http://localhost:3001/admin_home';
                }
            });
        })
}

