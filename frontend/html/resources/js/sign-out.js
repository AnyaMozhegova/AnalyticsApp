function signOut(event) {
    event.preventDefault();

    Swal.fire({
        title: 'Are you sure?',
        text: 'Do you want to sign out?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, sign out!'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch('http://localhost:8001/sign-out', {
                method: 'POST',
                credentials: 'include'
            })
                .then(response => {
                    if (response.ok) {
                        return response.json()
                    }
                })
                .then(() => {
                    Swal.fire({
                        title: 'Signed Out!',
                        text: 'You have been successfully signed out.',
                        icon: 'success',
                        confirmButtonText: 'OK'
                    }).then(() => window.location.href = 'http://localhost:3001/login'
                    )
                })
        }
    })
}

document.getElementById('exit').addEventListener('click', signOut);
