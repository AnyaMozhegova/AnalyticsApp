function addCell(tr, content) {
    const td = document.createElement('td');
    td.innerHTML = content;
    td.className = "text-l font-l pr-4"
    tr.appendChild(td);
}


function fetchAndStoreCustomers() {
    return fetch('http://localhost:8001/customer/', {credentials: 'include'})
        .then(response => response.json())
        .then(customers => {
            allCustomers = customers;
        })
        .catch(error => console.error("Error fetching customers:", error));
}

function loadCustomers(customersBody) {
    customersBody.innerHTML = '';
    allCustomers.forEach(customer => {
        const rowId = `customer-${customer._id}`;
        const tr = document.createElement('tr');
        tr.setAttribute('id', rowId);
        addCell(tr, customer.name);
        addCell(tr, customer.email);
        addCell(tr, `<button class="delete-btn text-l font-xl text-red-500 hover:text-red-700" onclick="deactivateCustomer('${customer._id}', '${rowId}')">Deactivate</button>`);
        customersBody.appendChild(tr);
    });
}

function deleteCustomerInit() {
    window.deactivateCustomer = function (customerId, rowId) {
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
                const deleteUrl = `http://localhost:8001/customer/${customerId}`;
                fetch(deleteUrl, {
                    method: 'DELETE',
                    credentials: "include"
                })
                    .then(response => {
                        if (response.ok) {
                            document.getElementById(rowId).remove();
                            allCustomers = allCustomers.filter(customer => customer._id !== parseInt(customerId));
                            Swal.fire(
                                'Deactivated!',
                                'The customer has been deactivated.',
                                'success'
                            );
                        } else if (response.status === 404) {
                            Swal.fire({
                                    title: 'Error!',
                                    text: 'Sorry, the customer is not found',
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

let allCustomers = [];

function init() {
    const customersBody = document.getElementById('customers-body');

    admin.get().then(() => {
        fetchAndStoreCustomers().then(() => {
            loadCustomers(customersBody);
        });
        deleteCustomerInit();
    })
}

document.addEventListener('DOMContentLoaded', init);