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

function signUp() {
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const passwordConfirm = document.getElementById("password_confirm").value;

    fetch("http://localhost:8001/customer/sign-up", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            name: name,
            email: email,
            password: password,
            password_confirm: passwordConfirm
        },),
        credentials: "include"
    })
        .then(response => {
                if (response.status === 400) {
                    Swal.fire({
                        title: 'Error!',
                        text: 'Your data are invalid or account with this email already exists. Make sure data fit input rules',
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
                } else return response.json()
            }
        )
        .then(response => {
            Swal.fire({
                title: 'Success!',
                text: 'Login is successful!',
                icon: 'success',
                confirmButtonText: 'OK'
            }).then((result) => {
                if (result.isConfirmed) {
                    if (response.role === "customer") window.location.href = 'http://localhost:3001/home';
                    else if (response.role === "admin") window.location.href = 'http://localhost:3001/admin-home';
                }
            });
        })
}

