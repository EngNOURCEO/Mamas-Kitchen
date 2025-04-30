document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();
    const errorElement = document.getElementById('error-message');
    
    errorElement.textContent = '';
    const submitButton = e.target.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = 'LOGGING IN...';

    try {
        // 1. Attempt login
        const loginResponse = await fetch('http://127.0.0.1:5000/login', {  // Use consistent address
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
            credentials: 'include'
        });

        if (!loginResponse.ok) {
            const errorData = await loginResponse.json();
            throw new Error(errorData.message || 'Login failed');
        }

        const loginData = await loginResponse.json();
        console.log('Login success:', loginData);

        // 2. Verify session
        const sessionCheck = await fetch('http://127.0.0.1:5000/check_session', {
            credentials: 'include'
        });
        
        const sessionData = await sessionCheck.json();
        console.log('Session data:', sessionData);
        
        if (!sessionData.logged_in) {
            throw new Error('Session not maintained');
        }

        // 3. Store user data
        localStorage.setItem('user_id', loginData.user_id);
        localStorage.setItem('user_type', loginData.user_type);
        localStorage.setItem('user_name', loginData.name);

        // 4. Redirect - use absolute URL to be safe
        window.location.href = 'http://127.0.0.1:5501/mamas_kitchen/html/homepage.html';

    } catch (error) {
        console.error('Login error:', error);
        errorElement.textContent = error.message;
        
        // Visual feedback
        errorElement.style.display = 'block';
        errorElement.style.animation = 'shake 0.5s';
        setTimeout(() => {
            errorElement.style.animation = '';
        }, 500);
        
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = 'LOGIN';
    }
});