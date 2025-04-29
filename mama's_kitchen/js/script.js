document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorElement = document.getElementById('error-message');
    
    // Clear previous errors
    errorElement.textContent = '';
    
    // Add loading state
    const submitButton = e.target.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = 'LOGGING IN...';
    
    try {
        const response = await fetch('http://127.0.0.1:5000/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                email: email, 
                password: password 
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store cook data in localStorage
            localStorage.setItem('cook_id', data.cook_id);
            localStorage.setItem('cook_name', data.name);
            
            // Redirect to cook's dashboard
            window.location.href = 'html/homepage.html';
        } else {
            errorElement.textContent = data.message || 'Invalid email or password';
            // Shake animation for error
            errorElement.style.animation = 'shake 0.5s';
            setTimeout(() => {
                errorElement.style.animation = '';
            }, 500);
        }
    } catch (error) {
        errorElement.textContent = 'Network error. Please try again.';
        console.error('Error:', error);
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = 'LOGIN';
    }
});