document.getElementById('registerForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const gender = document.getElementById('gender').value;
    const location = document.getElementById('location').value;
    const phone = document.getElementById('phone').value;
    
    const errorElement = document.getElementById('error-message');
    const successElement = document.getElementById('success-message');
    
    // Clear messages
    errorElement.textContent = '';
    successElement.textContent = '';
    
    // Add loading state
    const submitButton = e.target.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = 'REGISTERING...';
    
    try {
        const response = await fetch('http://127.0.0.1:5000/cook/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                name: name,
                email: email, 
                password: password,
                gender: gender,
                location: location,
                phone: phone
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            successElement.textContent = 'Registration successful! Redirecting...';
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1500);
        } else {
            errorElement.textContent = data.message || 'Registration failed';
            errorElement.style.animation = 'shake 0.5s';
            setTimeout(() => errorElement.style.animation = '', 500);
        }
    } catch (error) {
        errorElement.textContent = 'Network error. Please try again.';
        console.error('Error:', error);
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = 'REGISTER AS COOK';
    }
});