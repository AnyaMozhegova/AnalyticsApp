function displayDate(data) {
    let dateUploadedElement = document.getElementById("dateUploaded");
    let date = new Date(data.date_uploaded.$date);
    const options = {
        year: 'numeric', month: 'long', day: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit',
        hour12: false
    };
    dateUploadedElement.innerHTML = date.toLocaleString('en-US', options);
}

function displayDatasetLink(data) {
    let datasetLinkElement = document.getElementById("datasetLink");
    datasetLinkElement.href = `http://localhost:8001/report/${data._id}/file`;
}

function displayFitsCorrelation(data) {
    let fitsCorrelationElement = document.getElementById("fitsCorrelation");
    fitsCorrelationElement.innerHTML = data.fits_correlation_analysis ?
        "Fits correlation analysis" :
        "Does not fit correlation analysis";
}

function displayFitsDiscriminant(data) {
    let fitsDiscriminantElement = document.getElementById("fitsDiscriminant")
    fitsDiscriminantElement.innerHTML = data.fits_discriminant_analysis ?
        "Fits discriminant analysis" :
        "Does not fit discriminant analysis";
}

function processWorksheetForChart(worksheet) {
    let data = {labels: [], datasets: []};
    let ref = worksheet['!ref'];
    let range = XLSX.utils.decode_range(ref);

    for (let C = range.s.c; C <= range.e.c; ++C) {
        let columnData = [];
        let label = null;
        for (let R = range.s.r; R <= range.e.r; ++R) {
            let cell_ref = XLSX.utils.encode_cell({c: C, r: R});
            if (R === range.s.r) {
                label = worksheet[cell_ref].v;
                data.labels.push(label);
            } else {
                let cell = worksheet[cell_ref];
                columnData.push(cell ? cell.v : null);
            }
        }
        if (label) {
            data.datasets.push({
                label: label,
                data: columnData,
                backgroundColor: getRandomPastelColor(),
                borderColor: getRandomPastelColor(),
                borderWidth: 1
            });
        }
    }

    return data;
}

function getRandomPastelColor() {
    let r = (Math.round(Math.random() * 127) + 127).toString(16);
    let g = (Math.round(Math.random() * 127) + 127).toString(16);
    let b = (Math.round(Math.random() * 127) + 127).toString(16);
    r = r.length === 1 ? '0' + r : r;
    g = g.length === 1 ? '0' + g : g;
    b = b.length === 1 ? '0' + b : b;

    return `#${r}${g}${b}`;
}


function renderChart(data) {
    const ctx = document.getElementById('reportChart').getContext('2d');
    const reportChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            title: {
                display: true,
                text: 'Report Data Overview'
            },
            scales: {
                xAxes: [{stacked: true}],
                yAxes: [{stacked: true}]
            }
        }
    });
}

function fetchAndProcessXlsForChart(url) {
    fetch(url, {
        credentials: "include"
    })
        .then(response => {
            if (response.status === 404) {
                Swal.fire({
                        title: 'Error!',
                        text: 'Sorry, the report is not found',
                        icon: 'error',
                        confirmButtonText: 'OK'
                    }
                ).then(() => {
                    window.location.href = 'http://localhost:3001/home'
                })
            } else if (response.status === 500) {
                Swal.fire({
                        title: 'Server Error!',
                        text: 'An error occurred on the server. Please try again later.',
                        icon: 'error',
                        confirmButtonText: 'OK'
                    }
                ).then(() => {
                    window.location.href = 'http://localhost:3001/home'
                })
            } else if (response.status === 200) {
                return response.blob()
            }
        })
        .then(blob => {
            const reader = new FileReader();
            reader.onload = function (e) {
                const data = new Uint8Array(e.target.result);
                const workbook = XLSX.read(data, {type: 'array'});
                const firstSheetName = workbook.SheetNames[0];
                const worksheet = workbook.Sheets[firstSheetName];
                document.getElementById('xlsPreview').innerHTML = XLSX.utils.sheet_to_html(worksheet, {editable: false});

                const chartData = processWorksheetForChart(worksheet);
                renderChart(chartData);
            };
            reader.readAsArrayBuffer(blob);
        })
}


function deleteReport(reportId) {
    const deleteUrl = `http://localhost:8001/report/${reportId}`;
    fetch(deleteUrl, {
        method: 'DELETE',
        credentials: "include"
    })
        .then(response => {
            if (response.ok) {
                Swal.fire(
                    {
                        title: 'Deleted!',
                        text: 'The report has been successfully deleted!',
                        icon: 'success',
                        confirmButtonText: 'OK'
                    }
                ).then(() => {
                    window.location.href = 'http://localhost:3001/home';
                })
            } else if (response.status === 404) {
                Swal.fire({
                        title: 'Error!',
                        text: 'Sorry, the report is not found',
                        icon: 'error',
                        confirmButtonText: 'OK'
                    }
                ).then(() => {
                    window.location.href = 'http://localhost:3001/home'
                })
            } else if (response.status === 500) {
                Swal.fire({
                        title: 'Server Error!',
                        text: 'An error occurred on the server. Please try again later.',
                        icon: 'error',
                        confirmButtonText: 'OK'
                    }
                ).then(() => {
                    window.location.href = 'http://localhost:3001/home'
                })
            }
        })
        .catch(error => console.error('Error:', error));
}

function displayIndicatorValues(reportId) {
    fetch(`http://localhost:8001/report/${reportId}/indicator_values`, {
        method: 'GET',
        credentials: "include"
    })
        .then(response => {
                if (response.status === 404) {
                    Swal.fire({
                        title: 'Error!',
                        text: 'Sorry, the report is not found',
                        icon: 'error',
                        confirmButtonText: 'OK'
                    })
                } else
                    return response.json()
            }
        ).then(data => {
            const table = document.createElement('table');
            table.className = 'min-w-full leading-normal table-fixed';

            let allStats = new Set();
            Object.values(data).forEach(column => {
                column.forEach(statPair => {
                    allStats.add(statPair[1]);
                });
            });
            const statsOrder = Array.from(allStats);

            let thead = document.createElement('thead');
            let headerRow = document.createElement('tr');
            headerRow.innerHTML = `<th class="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"></th>`; // Empty first cell for column names
            statsOrder.forEach(stat => {
                headerRow.innerHTML += `<th class="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">${stat}</th>`;
            });
            thead.appendChild(headerRow);
            table.appendChild(thead);


            let tbody = document.createElement('tbody');
            Object.entries(data).forEach(([columnName, values]) => {
                let row = document.createElement('tr');
                row.innerHTML = `<td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">${columnName}</td>`;
                let valueMap = new Map(values.map(([value, stat]) => [stat, value]));
                statsOrder.forEach(stat => {
                    let cellValue = valueMap.has(stat) ? valueMap.get(stat) : '';
                    if (typeof cellValue === 'number') {
                        let decimalDigits = (cellValue.toString().split('.')[1] || '').length;
                        if (decimalDigits > 4) {
                            cellValue = cellValue.toFixed(4);
                        }
                    }
                    row.innerHTML += `<td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">${cellValue}</td>`;
                });
                tbody.appendChild(row);
            });
            table.appendChild(tbody);

            document.getElementById('indicatorValuesTable').appendChild(table);
        })
}


function init() {
    const reportId = window.location.pathname.split('/').pop();
    const apiUrl = `http://localhost:8001/report/${reportId}`;
    fetch(apiUrl, {
        method: 'GET',
        credentials: "include"
    })
        .then(response => {
            if (response.status === 500) {
                Swal.fire({
                    title: 'Server Error!',
                    text: 'An error occurred on the server. Please try again later.',
                    icon: 'error',
                    confirmButtonText: 'OK'
                }).then(() => {
                    window.location.href = 'http://localhost:3001/home'
                })
            } else if (response.status === 404) {
                Swal.fire({
                    title: 'Error!',
                    text: 'Sorry, the report is not found',
                    icon: 'error',
                    confirmButtonText: 'OK'
                }).then(() => {
                    window.location.href = 'http://localhost:3001/home'
                })
            }
            return response.json();
        })
        .then(data => {
            displayDate(data)
            displayDatasetLink(data)
            displayFitsCorrelation(data)
            displayFitsDiscriminant(data)
            displayIndicatorValues(reportId);
            if (data.report_link) {
                fetchAndProcessXlsForChart(`http://localhost:8001/report/${data._id}/file`);
            }
            document.getElementById('deleteReport').addEventListener('click', function () {
                Swal.fire({
                    title: 'Are you sure?',
                    text: "You won't be able to revert this!",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#3085d6',
                    cancelButtonColor: '#d33',
                    confirmButtonText: 'Yes, delete it!'
                }).then((result) => {
                    if (result.isConfirmed) {
                        deleteReport(reportId);
                    }
                });
            });
        })
}

document.addEventListener('DOMContentLoaded', init);
