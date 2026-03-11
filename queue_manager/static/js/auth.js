/**
 * Authentication and Account Security Logic
 * Handles real-time password strength validation.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Select the primary password input (ignores password confirmation)
    const passwordInput = document.querySelector('input[type="password"]:not([name*="pharma"])');
    
    if (passwordInput) {
        const strengthBar = document.getElementById('strengthBar');
        const strengthText = document.getElementById('strengthText');

        /**
         * Real-time calculation of password complexity
         */
        passwordInput.addEventListener('input', () => {
            const val = passwordInput.value;
            let score = 0;
            
            // Criteria for a secure password
            if (val.length > 5) score++;            // Basic length
            if (val.length > 8) score++;            // Good length
            if (/[A-Z]/.test(val)) score++;        // Uppercase required
            if (/[0-9]/.test(val)) score++;        // Numbers required
            if (/[^A-Za-z0-9]/.test(val)) score++;  // Symbols required

            // Mapping scores to visual feedback
            let color = '#ef4444'; // Red (Weak)
            let label = 'Weak';
            let width = '20%';

            if (score === 0) { 
                width = '0%'; 
                label = 'Enter password'; 
                color = 'var(--text-muted)'; 
            }
            else if (score < 3) { 
                width = '33%'; 
                color = '#f97316'; // Orange (Medium)
                label = 'Medium'; 
            }
            else if (score < 4) { 
                width = '66%'; 
                color = '#eab308'; // Amber (Strong)
                label = 'Strong'; 
            }
            else { 
                width = '100%'; 
                color = '#10b981'; // Emerald (Optimal)
                label = 'Very Strong'; 
            }

            // Apply visual updates to the strength meter
            if (strengthBar) {
                strengthBar.style.width = width;
                strengthBar.style.backgroundColor = color;
            }
            if (strengthText) {
                strengthText.textContent = label;
                strengthText.style.color = color;
            }
        });
    }
});
