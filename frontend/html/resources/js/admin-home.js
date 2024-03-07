function addCell(tr, content) {
    const td = document.createElement('td');
    td.innerHTML = content;
    td.className = "text-l font-l pr-4"
    tr.appendChild(td);
}


function fetchAndStoreAdmins() {
    return fetch('http://localhost:8001/admin/', {credentials: 'include'})
        .then(response => response.json())
        .then(admins => {
            allAdmins = admins;
        })
        .catch(error => console.error("Error fetching admins:", error));
}

function setupFilter(currentUser, adminsBody) {
    const filterToggle = document.getElementById('filter-toggle');
    const filterText = filterToggle.querySelector('span');

    filterToggle.onclick = function () {
        const isFiltering = filterText.textContent.includes('Show All Admins');
        loadAdmins(currentUser, adminsBody, !isFiltering);
        filterText.textContent = isFiltering ? 'Show My Subordinates' : 'Show All Admins';
    };
}


function loadAdmins(currentUser, adminsBody, filterSubordinates) {
    adminsBody.innerHTML = '';
    allAdmins.forEach(admin => {
        if (admin._id !== currentUser && (!filterSubordinates || admin.parent_admin === currentUser)) {
            const rowId = `admin-${admin._id}`;
            const tr = document.createElement('tr');
            tr.setAttribute('id', rowId);
            addCell(tr, admin.name);
            addCell(tr, admin.email);
            if (admin.parent_admin === currentUser) {
                addCell(tr, `<button class="delete-btn text-l font-xl text-red-500 hover:text-red-700" onclick="deactivateAdmin('${admin._id}', '${rowId}')">Deactivate</button>`);
            } else {
                addCell(tr, '');
            }
            adminsBody.appendChild(tr);
        }
    });
}

function deleteAdminInit() {
    window.deactivateAdmin = function (adminId, rowId) {
        Swal.fire({
            title: 'Are you sure?',
            text: "You won't be able to revert this!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, deactivate it!'
        }).then((result) => {
            if (result.isConfirmed) {
                const deleteUrl = `http://localhost:8001/admin/${adminId}`;
                fetch(deleteUrl, {
                    method: 'DELETE',
                    credentials: "include"
                })
                    .then(response => {
                        if (response.ok) {
                            document.getElementById(rowId).remove();
                            allAdmins = allAdmins.filter(admin => admin._id !== parseInt(adminId));
                            Swal.fire(
                                'Deactivated!',
                                'The admin has been deactivated.',
                                'success'
                            );
                        } else if (response.status === 404) {
                            Swal.fire({
                                    title: 'Error!',
                                    text: 'Sorry, the admin is not found',
                                    icon: 'error',
                                    confirmButtonText: 'OK'
                                }
                            ).then(() => window.location.href = 'http://localhost:3001/admin-home')
                        } else if (response.status === 500) {
                            Swal.fire({
                                    title: 'Server Error!',
                                    text: 'An error occurred on the server. Please try again later.',
                                    icon: 'error',
                                    confirmButtonText: 'OK'
                                }
                            ).then(() => window.location.href = 'http://localhost:3001/admin-home')
                        }
                    })
            }
        })
    }
}

let allAdmins = [];

function init() {
    const adminsBody = document.getElementById('admins-body');

    admin.get().then(admin => {
        let currentUser = admin._id;
        fetchAndStoreAdmins().then(() => {
            loadAdmins(currentUser, adminsBody, false);
            setupFilter(currentUser, adminsBody);
        });
        deleteAdminInit();
    })
}

document.addEventListener('DOMContentLoaded', init);