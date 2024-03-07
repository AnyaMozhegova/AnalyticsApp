function adminCreate() {
    admin.get().then(admin => {
        let currentUser = admin._id;
        const name = document.getElementById("name").value;
        const email = document.getElementById("email").value;

        fetch("http://localhost:8001/admin/create", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                email: email,
                parent_admin: currentUser
            }),
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
                    text: 'Admin has been successfully created!',
                    icon: 'success',
                    confirmButtonText: 'OK'
                }).then((result) => {
                    if (result.isConfirmed) {
                        const adminPasswordContainer = document.getElementById("generated-password-container");
                        adminPasswordContainer.classList.remove("hidden");

                        const adminPassword = response.admin_password;
                        let adminPasswordElement = document.getElementById("generated-password");
                        adminPasswordElement.textContent = adminPassword;

                        const copyBtn = document.getElementById('copy-password');
                        if (copyBtn) {
                            copyBtn.addEventListener('click', (event) => {
                                const passwordText = document.getElementById('generated-password').textContent;
                                navigator.clipboard.writeText(passwordText).then(() =>
                                    Swal.fire('Copied!', 'The generated password has been copied to clipboard.', 'success'))
                                event.preventDefault();
                                event.stopPropagation();
                            });
                        }
                    }
                });
            })
    })
}
