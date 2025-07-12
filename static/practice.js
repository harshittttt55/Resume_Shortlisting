const form = document.getElementById('signupForm');
const passwordInput = document.getElementById('password');
const confirmpasswordInput = document.getElementById('confirmPassword');
const errorElement = document.getElementById('error');


form.addEventListener('submit', function (e) {
    e.preventDefault();
    const password = passwordInput.value;
    const confirmpassword = confirmpasswordInput.value;
    console.log(password);
    errorElement.textContent = '';
    errorElement.style.color = 'red';  

    if (password.length < 8) {
        errorElement.textContent = 'Password must be at least 8 characters.';
    }
    else if (!/[A-Z]/.test(password)) {
        errorElement.textContent = 'Password must contain at least one uppercase letter.';
    }
    else if (!/[a-z]/.test(password)) {
        errorElement.textContent = 'Password must contain at least one lowercase letter.';
    }
    else if (!/[0-9]/.test(password)) {
        errorElement.textContent = 'Password must contain at least one number.';
    }
    else if (!/[@#$%^&*()!+_\-=\[\]{};':"\\|,.<>\/?]+/.test(password)) {
        errorElement.textContent = 'Password must contain at least one special character (@, #, $, %, ^, &, *, etc.).';
    }
    else if (password !== confirmpassword) {
        errorElement.textContent = 'Your password does not match.';
    }
    else {
        errorElement.textContent = '';
        alert('Signup Successful!');
        form.reset(); 
    }
});
