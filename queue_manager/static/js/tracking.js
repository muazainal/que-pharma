/**
 * Patient Tracking Logic
 * Handles real-time status polling, UI updates, and notification triggers.
 */

document.addEventListener('DOMContentLoaded', () => {
    // These variables must be global or passed from the template
    // We expect window.ticketId to be set in the script block of the HTML
    const ticketId = window.ticketId;
    if (!ticketId) return;

    // DOM Element References
    const statusText = document.getElementById('statusText');
    const statusPulse = document.getElementById('statusPulse');
    const statusCard = document.getElementById('statusCard');
    const circleDisplay = document.getElementById('circleDisplay');
    const notificationSound = document.getElementById('notificationSound');
    const countdownEl = document.getElementById('countdown');
    
    // Notification & Contact elements
    const savePhoneBtn = document.getElementById('savePhoneBtn');
    const phoneUpdate = document.getElementById('phoneUpdate');
    const whatsappSection = document.getElementById('whatsappSection');
    const phoneInputArea = document.getElementById('phoneInputArea');
    const notifyText = document.getElementById('notifyText');

    let lastStatus = window.initialStatus || "Preparing";
    let countdown = 10;

    /**
     * Updates the visual state of the tracking page based on current status
     * @param {string} status - 'Preparing', 'Ready', or 'Collected'
     */
    function updateUI(status) {
        statusText.textContent = status;
        
        if (status === 'Preparing') {
            // Amber palette for preparation phase
            statusText.style.color = '#F59E0B';
            statusPulse.style.background = '#F59E0B';
            statusCard.classList.remove('status-ready-glow');
            circleDisplay.style.borderColor = 'rgba(245, 158, 11, 0.3)';
        } else if (status === 'Ready') {
            // Emerald palette + Glow for completion phase
            statusText.style.color = '#10B981';
            statusPulse.style.background = '#10B981';
            statusCard.classList.add('status-ready-glow');
            circleDisplay.style.borderColor = 'rgba(16, 185, 129, 0.6)';
            circleDisplay.classList.add('animate__animated', 'animate__pulse', 'animate__infinite');
            
            // Critical Feedback: Play sound and vibrate ONLY when status first changes to Ready
            if (lastStatus !== 'Ready') {
                notificationSound.play().catch(e => console.log('Autoplay blocked:', e));
                if (navigator.vibrate) navigator.vibrate([200, 100, 200]);
            }
        } else if (status === 'Collected') {
            // Gray/Muted palette for archvied phase
            statusText.style.color = '#9CA3AF';
            statusPulse.style.background = '#9CA3AF';
            statusCard.classList.remove('status-ready-glow');
            circleDisplay.style.borderColor = 'var(--card-border)';
            circleDisplay.classList.remove('animate__animated', 'animate__pulse', 'animate__infinite');
        }
        
        lastStatus = status;
    }

    /**
     * Handles patient phone number updates for voluntary notifications
     */
    if (savePhoneBtn) {
        savePhoneBtn.addEventListener('click', () => {
            const phone = phoneUpdate.value.trim();
            if (!phone) return;

            fetch(`/api/update-contact/${ticketId}/`, {
                method: 'POST',
                body: JSON.stringify({ phone_number: phone }),
                headers: { 'Content-Type': 'application/json' }
            })
            .then(res => res.json())
            .then(data => {
                if(data.status === 'success') {
                    // Update UI to reflect subscription success
                    phoneInputArea.style.display = 'none';
                    notifyText.textContent = "Great! You are now subscribed to updates.";
                    whatsappSection.style.display = 'block';
                    
                    // Update the direct WhatsApp link with the new number
                    const waBtn = document.getElementById('whatsappBtn');
                    const currentHref = waBtn.href;
                    waBtn.href = currentHref.replace(/wa\.me\/(\w*)\?/, `wa.me/${phone}?`);
                }
            })
            .catch(err => console.error('Failed to update phone number:', err));
        });
    }

    /**
     * Polls the server for status updates every 10 seconds
     */
    function checkStatus() {
        countdown = 10;
        fetch(`/api/check-status/${ticketId}/`)
            .then(res => res.json())
            .then(data => {
                updateUI(data.status);
            })
            .catch(err => console.error('Status check failed:', err));
    }

    // Refresh count-down visual helper
    setInterval(() => {
        countdown--;
        if (countdown < 0) countdown = 10;
        if (countdownEl) countdownEl.textContent = countdown;
    }, 1000);

    // Initial UI Setup
    updateUI(lastStatus);
    
    // Heartbeat for real-time status tracking
    setInterval(checkStatus, 10000);
});
