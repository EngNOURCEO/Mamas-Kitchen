document.getElementById('registerForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorElement = document.getElementById('error-message');
    const successElement = document.getElementById('success-message');
    
    // Clear messages
    errorElement.textContent = '';
    successElement.textContent = '';
    
    // Loading state
    const submitButton = e.target.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = 'CREATING ACCOUNT...';
    
    try {
        const response = await fetch('http://127.0.0.1:5000/customer/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                name: name,
                email: email, 
                password: password 
            })
        });

        // First check if response exists
        if (!response) {
            throw new Error('No response from server');
        }

        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            throw new Error(`Invalid response: ${text}`);
        }

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Registration failed');
        }

        successElement.textContent = data.message || 'Account created successfully!';
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1500);
        
    } catch (error) {
        console.error('Registration error:', error);
        errorElement.textContent = error.message || 'Network error. Please try again.';
        errorElement.style.animation = 'shake 0.5s';
        setTimeout(() => errorElement.style.animation = '', 500);
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = 'CREATE ACCOUNT';
    }
});