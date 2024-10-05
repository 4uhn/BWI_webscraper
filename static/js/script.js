const form = document.getElementById('dataForm');
const runCodeBtn = document.getElementById('runCode');
const downloadExcelBtn = document.getElementById('downloadExcel');
const selects = document.querySelectorAll('select');
let isProcessing = false;

function checkFormValidity() {
    const isValid = Array.from(selects).every(select => select.value !== '');
    runCodeBtn.disabled = !isValid;
}

selects.forEach(select => {
    select.addEventListener('change', checkFormValidity);
});

runCodeBtn.addEventListener('click', function(e) {
    e.preventDefault();
    if (isProcessing) return;

    isProcessing = true;
    runCodeBtn.disabled = true;
    downloadExcelBtn.disabled = true;

    const formData = new FormData(form);
    fetch('/scrape', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if (data.file_path) {
            downloadExcelBtn.disabled = false;
            downloadExcelBtn.onclick = function(e){
                e.preventDefault();
                window.location.href = '/download/' + encodeURIComponent(data.file_path);
            }
        } else {
            console.error('No file path received from server');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    })
    .finally(() => {
        isProcessing = false;
        checkFormValidity();
    });
});

const formElements = document.querySelectorAll('select, button');
formElements.forEach((element, index) => {
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    setTimeout(() => {
        element.style.transition = 'all 0.5s ease';
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
    }, 100 * (index + 1));
});