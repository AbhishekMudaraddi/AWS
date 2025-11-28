document.getElementById('userForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const responseDiv = document.getElementById('response');
    
    try {
        const response = await fetch('/submit', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            responseDiv.className = 'success';
            responseDiv.textContent = result.message;
            this.reset();
        } else {
            responseDiv.className = 'error';
            responseDiv.textContent = result.message;
        }
    } catch (error) {
        responseDiv.className = 'error';
        responseDiv.textContent = 'An error occurred. Please try again.';
    }
});