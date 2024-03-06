function previewFile() {
    const file = document.getElementById('fileInput').files[0];
    const preview = document.getElementById('filePreview');
    const contentPreview = document.getElementById('fileContentPreview');
    const confirmBtn = document.getElementById('confirmBtn');

    if (file) {
        preview.textContent = `Selected file: ${file.name}`;
        const reader = new FileReader();
        reader.onload = function (e) {
            const data = new Uint8Array(e.target.result);
            const workbook = XLSX.read(data, {type: 'array'});

            const firstSheetName = workbook.SheetNames[0];
            const worksheet = workbook.Sheets[firstSheetName];
            contentPreview.innerHTML = XLSX.utils.sheet_to_html(worksheet, {editable: false});
        };
        reader.readAsArrayBuffer(file);

        confirmBtn.classList.remove('hidden');
    } else {
        preview.textContent = '';
        contentPreview.innerHTML = '';
        confirmBtn.classList.add('hidden');
    }
}


async function confirmUpload() {
    const file = document.getElementById('fileInput').files[0];
    const url = `http://localhost:8001/customer/upload_report`;
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append('report', file)
    xhr.open('POST', url, true)
    xhr.withCredentials = true;
    xhr.addEventListener('readystatechange', function (e) {
        if (xhr.readyState === 4 && xhr.status === 200) {
            Swal.fire({
                title: 'Success!',
                text: 'Dataset has been successfully uploaded!',
                icon: 'success',
                confirmButtonText: 'OK'
            })
            setTimeout(() => window.location.replace('http://localhost:3001/home'),
                1000)
        } else if (xhr.readyState === 4 && xhr.status === 500) {
            Swal.fire({
                title: 'Server Error!',
                text: 'An error occurred on the server. Please try again later.',
                icon: 'error',
                confirmButtonText: 'OK'
            })
        } else if (xhr.readyState === 4 && xhr.status === 400) {
            Swal.fire({
                title: 'Error!',
                text: 'File has incorrect data. Make sure first raw is column names and other raws contain only numeric data',
                icon: 'error',
                confirmButtonText: 'OK'
            })
        }
    });
    xhr.send(formData)
}

document.getElementById('confirmBtn').addEventListener('click', confirmUpload);