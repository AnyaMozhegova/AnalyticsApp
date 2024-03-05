function appendDate(row, data) {
    const dateCell = document.createElement('td');
    let date = new Date(data.date_uploaded);
    const year = date.getFullYear()
    const monthName = new Intl.DateTimeFormat('en-US', {month: 'long'}).format(date)
    const day = date.getDate()
    dateCell.textContent = `${day} ${monthName} ${year}`
    row.appendChild(dateCell);
}

function appendReportLink(row, data) {
    const reportLinkCell = document.createElement('td');
    const link = document.createElement('a');
    link.href = data.report_link;
    link.textContent = 'Download report';
    reportLinkCell.appendChild(link);
    row.appendChild(reportLinkCell);
}

function appendViewHyperlink(row, data) {
    const hyperlinkCell = document.createElement('td');
    const link = document.createElement('a');
    link.href = `http://localhost:3001/report/${data.id}`
    link.textContent = 'View report';
    hyperlinkCell.appendChild(link);
    row.appendChild(hyperlinkCell);
}

async function init() {
    await fetch("http://localhost:8001/report/", {
        method: 'GET',
        credentials: "include"
    }).then(async response => {
        if (response.status === 500) {
            Swal.fire({
                title: 'Error!',
                text: 'User data is incorrect. Make sure the fields are not empty and your account exists',
                icon: 'error',
                confirmButtonText: 'OK'
            });
        } else return await response.json()
    }).then(response => {
        const tableBody = document.getElementById('reports-body');
        while (tableBody.firstChild) {
            tableBody.removeChild(tableBody.firstChild);
        }
        response.forEach(data => {
            const row = document.createElement('tr');
            appendDate(row, data);
            appendReportLink(row, data);
            appendViewHyperlink(row, data);
            tableBody.appendChild(row);
        })

    })
}

document.addEventListener('DOMContentLoaded', init);