const loginForm = document.getElementById('loginForm'); 
const loginButton = document.getElementById('loginButton');
const errorMessage = document.getElementById('errorMessage');

loginButton.addEventListener('click', function(e) {
    e.preventDefault();
    loginButton.disabled = true;
    const formData = new FormData(loginForm);
    fetch('/login', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if(data.success) {
            window.location.href = '/home';
        } else {
            errorMessage.textContent = data.error;
            errorMessage.classList.add('visible');
            loginButton.disabled = false;
        };
    });
});