/**
 * Pharmacist Dashboard Logic
 * Handles real-time ticket fetching, status updates, and QR Generation.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Element References
    const ticketsBody = document.getElementById('ticketsBody');
    const addTicketForm = document.getElementById('addTicketForm');
    const qrImage = document.getElementById('qrImage');
    const qrPatientName = document.getElementById('qrPatientName');
    
    // Bootstrap Modal instances
    const qrModal = new bootstrap.Modal(document.getElementById('qrModal'));
    const addPatientModal = new bootstrap.Modal(document.getElementById('addPatientModal'));

    /**
     * Fetches the latest tickets from the API and updates the table
     */
    function fetchTickets() {
        fetch('/api/tickets/')
            .then(res => res.json())
            .then(data => {
                // Handle empty state
                if(data.tickets.length === 0) {
                    ticketsBody.innerHTML = '<tr><td colspan="8" class="text-center py-5 text-muted-modern">No active tickets found</td></tr>';
                    return;
                }
                
                // Clear table and rebuild rows
                ticketsBody.innerHTML = '';
                data.tickets.forEach(ticket => {
                    const statusClass = {
                        'Preparing': 'status-badge-preparing',
                        'Ready': 'status-badge-ready',
                        'Collected': 'status-badge-collected'
                    }[ticket.status] || '';

                    // WhatsApp Logic: Pre-fill messages based on status
                    let waBtn = '';
                    if (ticket.phone_number) {
                        const cleanPhone = ticket.phone_number.replace(/\D/g,'');
                        const msg = ticket.status === 'Preparing' 
                            ? 'Salam sejahtera, terima kasih, ubat anda sedang disedikan, harap sbar menunggu'
                            : 'Salam sejahtera, ubat anda sudah sedia untuk dituntut.';
                        const waUrl = `https://wa.me/${cleanPhone}?text=${encodeURIComponent(msg)}`;
                        
                        waBtn = `
                        <a href="${waUrl}" target="_blank" class="whatsapp-mini-btn" title="Notify WhatsApp">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                                <path d="M13.601 2.326A7.854 7.854 0 0 0 7.994 0C3.627 0 .068 3.558.064 7.926c0 1.399.366 2.76 1.057 3.965L0 16l4.204-1.102a7.933 7.933 0 0 0 3.79.965h.004c4.368 0 7.926-3.558 7.93-7.93A7.898 7.898 0 0 0 13.6 2.326zM7.994 14.521a6.573 6.573 0 0 1-3.356-.92l-.24-.144-2.494.654.666-2.433-.156-.251a6.56 6.56 0 0 1-1.007-3.505c0-3.626 2.957-6.584 6.591-6.584a6.56 6.56 0 0 1 4.66 1.931 6.557 6.557 0 0 1 1.928 4.66c-.004 3.639-2.961 6.592-6.592 6.592zm3.615-4.934c-.197-.099-1.17-.578-1.353-.646-.182-.065-.315-.099-.445.099-.133.197-.513.646-.627.775-.114.133-.232.148-.43.05-.197-.1-.836-.308-1.592-.985-.59-.525-.985-1.175-1.103-1.372-.114-.198-.011-.304.088-.403.087-.088.197-.232.296-.346.1-.114.133-.198.198-.33.065-.134.034-.248-.015-.347-.05-.099-.445-1.076-.612-1.47-.16-.389-.323-.335-.445-.34-.114-.007-.247-.007-.38-.007a.729.729 0 0 0-.529.247c-.182.198-.691.677-.691 1.654 0 .977.71 1.916.81 2.049.098.133 1.394 2.132 3.383 2.992.47.205.84.326 1.129.418.475.152.904.129 1.246.08.38-.058 1.171-.48 1.338-.943.164-.464.164-.86.114-.943-.049-.084-.182-.133-.38-.232z"/>
                            </svg>
                        </a>`;
                    }

                    const row = `
                        <tr class="animate__animated animate__fadeIn">
                            <td><span class="fw-bold" style="color:var(--accent-primary)">#${ticket.queue_number}</span></td>
                            <td><span class="patient-name-hl">${ticket.patient_name}</span></td>
                            <td>
                                <span class="text-muted-modern small">${ticket.phone_number || '<em class="opacity-50">Pending</em>'}</span>
                                ${waBtn}
                            </td>
                            <td><span class="badge badge-modern ${statusClass}">${ticket.status}</span></td>
                            <td><span class="text-muted-modern small">${ticket.pharmacist}</span></td>
                            <td><span class="text-muted-modern small">${ticket.created_at}</span></td>
                            <td>
                                <div class="status-stepper">
                                    <button class="btn text-warning" onclick="updateStatus('${ticket.id}', 'Preparing')">Prep</button>
                                    <button class="btn text-success" onclick="updateStatus('${ticket.id}', 'Ready')">Ready</button>
                                    <button class="btn text-secondary" onclick="updateStatus('${ticket.id}', 'Collected')">Collect</button>
                                </div>
                            </td>
                            <td class="text-end">
                                <div class="d-flex justify-content-end gap-2">
                                    <button class="action-btn" onclick="showQR('${ticket.id}', '${ticket.patient_name}')" title="Show QR">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1l-3 3m6-3l3 3M8 8h1a1 1 0 011 1v1a1 1 0 01-1 1H8a1 1 0 01-1-1V9a1 1 0 011-1zm1 4h-1a1 1 0 00-1 1v1a1 1 0 001 1h1a1 1 0 001-1v-1a1 1 0 00-1-1zm7-4h1a1 1 0 011 1v1a1 1 0 01-1 1h-1a1 1 0 01-1-1V9a1 1 0 011-1zm1 4h-1a1 1 0 00-1 1v1a1 1 0 001 1h1a1 1 0 001-1v-1a1 1 0 00-1-1z" />
                                        </svg>
                                    </button>
                                    <a href="/track/${ticket.id}/" target="_blank" class="action-btn" title="Track Page">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                        </svg>
                                    </a>
                                </div>
                            </td>
                        </tr>`;
                    ticketsBody.insertAdjacentHTML('beforeend', row);
                });
            })
            .catch(err => console.error('Failed to fetch tickets:', err));
    }

    /**
     * Shows a proactive notification toast with a WhatsApp link
     */
    function showNotification(result) {
        if (!result.phone_number) return;

        const toastEl = document.getElementById('statusToast');
        const toastActionArea = document.getElementById('toastActionArea');
        const toastMessage = document.getElementById('toastMessage');
        const bootstrapToast = new bootstrap.Toast(toastEl);

        const cleanPhone = result.phone_number.replace(/\D/g,'');
        const msg = result.new_status === 'Preparing' 
            ? 'Salam sejahtera, terima kasih, ubat anda sedang disedikan, harap sbar menunggu'
            : 'Salam sejahtera, ubat anda sudah sedia untuk dituntut.';
        const waUrl = `https://wa.me/${cleanPhone}?text=${encodeURIComponent(msg)}`;

        toastMessage.textContent = `${result.patient_name} is now marked as ${result.new_status}. Inform them?`;
        toastActionArea.innerHTML = `
            <a href="${waUrl}" target="_blank" class="btn-modern btn-primary-modern py-2 w-100" onclick="bootstrap.Toast.getInstance(document.getElementById('statusToast')).hide()">
                Send WhatsApp Now
            </a>
        `;

        bootstrapToast.show();
    }

    /**
     * Updates the status of a specific ticket via the API
     * @param {string} ticketId 
     * @param {string} newStatus 
     */
    window.updateStatus = (ticketId, newStatus) => {
        fetch(`/api/update-status/${ticketId}/`, {
            method: 'POST',
            body: JSON.stringify({ status: newStatus }),
            headers: { 'Content-Type': 'application/json' }
        })
        .then(res => res.json())
        .then(result => {
            if (result.status === 'success') {
                fetchTickets();
                showNotification(result);
            }
        })
        .catch(err => console.error('Status update failed:', err));
    };

    /**
     * Triggers the QR code modal for a given ticket
     * @param {string} ticketId 
     * @param {string} patientName 
     */
    window.showQR = (ticketId, patientName) => {
        qrImage.src = `/api/qr/${ticketId}/`;
        qrPatientName.textContent = `Patient: ${patientName}`;
        qrModal.show();
    };

    /**
     * Handles the submission of the new ticket form
     */
    addTicketForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(addTicketForm);
        const data = Object.fromEntries(formData.entries());

        fetch('/api/create-ticket/', {
            method: 'POST',
            body: JSON.stringify(data),
            headers: { 'Content-Type': 'application/json' }
        })
        .then(res => res.json())
        .then(result => {
            if(result.status === 'success') {
                // Hide modal and refresh list
                addPatientModal.hide();
                addTicketForm.reset();
                fetchTickets();
            } else {
                alert(result.message || 'Failed to create ticket');
            }
        })
        .catch(err => console.error('Failed to create ticket:', err));
    });

    /**
     * Automatic Suggestion for Next Ticket Number
     * Pre-fills the 'Ticket Number' field when the modal is opened.
     */
    document.getElementById('addPatientModal').addEventListener('show.bs.modal', () => {
        const manualInput = document.getElementById('manualQueueNumber');
        fetch('/api/tickets/')
            .then(res => res.json())
            .then(data => {
                let nextNum = 1;
                if (data.tickets.length > 0) {
                    // Extract all queue numbers to find the highest
                    const nums = data.tickets.map(t => parseInt(t.queue_number));
                    nextNum = Math.max(...nums) + 1;
                }
                manualInput.value = nextNum;
                manualInput.placeholder = nextNum;
            });
    });

    // Initial load
    fetchTickets();
    
    // Auto-refresh every 5 seconds to keep the queue live
    setInterval(fetchTickets, 5000);
});
