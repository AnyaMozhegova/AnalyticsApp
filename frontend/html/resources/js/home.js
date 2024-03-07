function appendDate(row, data) {
    const dateCell = document.createElement('td');
    let date = new Date(data.date_uploaded.$date);
    const options = {
        year: 'numeric', month: 'long', day: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit',
        hour12: false
    };
    dateCell.textContent = date.toLocaleString('en-US', options);
    dateCell.className = "text-l font-l pr-4";
    row.appendChild(dateCell);
}

function appendDatasetLink(row, data) {
    const reportLinkCell = document.createElement('td');
    const link = document.createElement('a');

    link.href = `http://localhost:8001/report/${data._id}/file`;
    link.textContent = 'Download dataset';
    link.className = "text-l font-l pr-4 text-blue-600 hover:underline";
    link.setAttribute('download', '');

    reportLinkCell.appendChild(link);
    row.appendChild(reportLinkCell);
}

function appendViewHyperlink(row, data) {
    const hyperlinkCell = document.createElement('td');
    const link = document.createElement('a');
    link.href = `http://localhost:3001/report/${data._id}`
    link.textContent = 'View';
    link.className = "font-bold text-l font-l pr-4";
    hyperlinkCell.appendChild(link);
    row.appendChild(hyperlinkCell);
}

async function init() {
    await fetch("http://localhost:8001/report/", {
        method: 'GET',
        credentials: "include"
    }).then(response => {
        if (response.status === 500) {
            Swal.fire({
                title: 'Server Error!',
                text: 'An error occurred on the server. Please try again later.',
                icon: 'error',
                confirmButtonText: 'OK'
            });
        }
        return response.json()
    }).then(async content => {
        const tableBody = document.getElementById('reports-body');
        while (tableBody.firstChild) {
            tableBody.removeChild(tableBody.firstChild);
        }
        for (let i = 0; i < content.length; i++) {
            const row = document.createElement('tr');
            const data = content[i]
            appendDate(row, data);
            appendDatasetLink(row, data);
            appendViewHyperlink(row, data);
            tableBody.appendChild(row);
        }

    })
}

document.addEventListener('DOMContentLoaded', init);