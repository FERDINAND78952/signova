/**
 * Payment form handling for Signova
 * This script handles the payment form interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    initPaymentForm();
});

/**
 * Initialize payment form
 */
function initPaymentForm() {
    // Get payment form elements
    const planCards = document.querySelectorAll('.plan-card');
    const processingMessage = document.querySelector('.payment-processing');
    
    if (planCards.length === 0) return;
    
    // Add click event to plan cards for selection
    planCards.forEach(card => {
        card.addEventListener('click', function() {
            // Remove active class from all cards
            planCards.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked card
            this.classList.add('active');
            
            // Find the button in this card and focus it
            const button = this.querySelector('button');
            if (button) button.focus();
        });
    });
    
    // Check if we have payment data from the server
    if (typeof paymentData !== 'undefined' && paymentData) {
        try {
            // Parse payment data if it's a string
            const data = typeof paymentData === 'string' ? JSON.parse(paymentData) : paymentData;
            
            // If we have payment data, initialize Flutterwave checkout
            if (data && data.public_key && data.tx_ref) {
                // Show processing message
                if (processingMessage) processingMessage.style.display = 'block';
                
                // Initialize Flutterwave checkout
                const flw = new FlutterwaveCheckout({
                    public_key: data.public_key,
                    tx_ref: data.tx_ref,
                    amount: data.amount,
                    currency: data.currency,
                    payment_options: "card, mobilemoney, ussd",
                    customer: data.customer,
                    customizations: data.customizations,
                    callback: function(response) {
                        // Handle successful payment
                        if (response.status === "successful") {
                            // Create form to submit transaction details
                            const form = document.createElement('form');
                            form.method = 'POST';
                            form.action = data.redirect_url || window.location.href;
                            
                            // Add CSRF token
                            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                            const csrfInput = document.createElement('input');
                            csrfInput.type = 'hidden';
                            csrfInput.name = 'csrfmiddlewaretoken';
                            csrfInput.value = csrfToken;
                            form.appendChild(csrfInput);
                            
                            // Add transaction reference
                            const txRefInput = document.createElement('input');
                            txRefInput.type = 'hidden';
                            txRefInput.name = 'tx_ref';
                            txRefInput.value = response.tx_ref;
                            form.appendChild(txRefInput);
                            
                            // Add transaction ID
                            const txIdInput = document.createElement('input');
                            txIdInput.type = 'hidden';
                            txIdInput.name = 'transaction_id';
                            txIdInput.value = response.transaction_id;
                            form.appendChild(txIdInput);
                            
                            // Submit the form
                            document.body.appendChild(form);
                            form.submit();
                        } else {
                            // Hide processing message
                            if (processingMessage) processingMessage.style.display = 'none';
                            
                            // Show error message
                            alert('Payment failed. Please try again.');
                        }
                    },
                    onclose: function() {
                        // Hide processing message when payment modal is closed
                        if (processingMessage) processingMessage.style.display = 'none';
                    }
                });
                
                // Open Flutterwave checkout
                flw.open();
            }
        } catch (error) {
            console.error('Error parsing payment data:', error);
        }
    }
}