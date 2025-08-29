/**
 * Flutterwave Payment Integration for Signova
 * This script handles the integration with Flutterwave payment gateway
 * Updated to use flutterwavedjango package
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Flutterwave payment buttons
    initFlutterwavePayment();
    
    // Initialize payment method selectors
    initPaymentMethodSelectors();
});

/**
 * Initialize payment method selectors
 */
function initPaymentMethodSelectors() {
    // Get all payment method buttons
    const methodButtons = document.querySelectorAll('.payment-method');
    
    if (methodButtons.length === 0) return;
    
    // Add click event to each payment method button
    methodButtons.forEach(button => {
        button.addEventListener('click', function() {
            const planId = this.dataset.plan;
            const method = this.dataset.method;
            
            // Remove active class from all buttons in the same group
            const siblings = document.querySelectorAll(`.payment-method[data-plan="${planId}"]`);
            siblings.forEach(sibling => sibling.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Update the payment button with the selected method
            const payButton = document.querySelector(`.flutterwave-pay[data-plan="${planId}"]`);
            if (payButton) {
                payButton.dataset.paymentMethod = method;
                
                // Update button text based on selected method
                if (method === 'mtn') {
                    payButton.innerHTML = '<img src="/static/images/mtn-momo.svg" alt="MTN MoMo" height="20"> Pay with MTN MoMo';
                } else {
                    payButton.innerHTML = '<i class="fas fa-credit-card"></i> Pay with Card';
                }
            }
        });
    });
    
    // Set default payment method to MTN MoMo
    const defaultMtnButtons = document.querySelectorAll('.payment-method[data-method="mtn"]');
    defaultMtnButtons.forEach(button => button.click());
}

/**
 * Initialize Flutterwave payment buttons
 */
function initFlutterwavePayment() {
    // Get all payment buttons with flutterwave-pay class
    const paymentButtons = document.querySelectorAll('.flutterwave-pay');
    
    if (paymentButtons.length === 0) return;
    
    // Add click event to each payment button
    paymentButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get payment details from data attributes
            const amount = this.dataset.amount || '0';
            const currency = this.dataset.currency || 'RWF';
            const description = this.dataset.description || 'Signova Subscription';
            const planId = this.dataset.plan || '';
            const customerEmail = this.dataset.email || '';
            const customerName = this.dataset.name || '';
            const paymentPlan = this.dataset.paymentPlan || '';
            const txRef = 'signova-' + generateTransactionRef();
            
            // Show loading state
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            this.disabled = true;
            
            // Initialize Flutterwave checkout
            makePayment({
                amount: parseFloat(amount),
                currency,
                description,
                planId,
                customerEmail,
                customerName,
                paymentPlan,
                txRef,
                button: this
            });
        });
    });
}

/**
 * Generate a unique transaction reference
 */
function generateTransactionRef() {
    return Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
}

/**
 * Make payment using Flutterwave
 */
function makePayment(paymentData) {
    // Check if FlutterwaveCheckout is available
    if (typeof FlutterwaveCheckout !== 'function') {
        console.error('Flutterwave SDK not loaded');
        resetButton(paymentData.button, 'Payment Error');
        return;
    }
    
    // Get the public key from the template
    const publicKey = window.flutterwavePublicKey || "FLWPUBK_TEST-YOUR-PUBLIC-KEY-HERE";
    
    // Get phone number for mobile money payments
    const paymentMethod = paymentData.button.dataset.paymentMethod || 'card';
    let phoneNumber = '';
    
    if (paymentMethod === 'mtn') {
        const planId = paymentData.button.dataset.plan;
        const phoneInput = document.getElementById(`phone-${planId}`);
        
        if (phoneInput) {
            phoneNumber = phoneInput.value.trim();
            
            // Validate phone number for MTN Mobile Money
            if (!phoneNumber) {
                alert('Please enter your phone number for MTN Mobile Money payment');
                resetButton(paymentData.button, paymentMethod === 'mtn' ? 'Pay with MTN MoMo' : 'Pay with Card');
                return;
            }
            
            // Format phone number if needed (remove spaces, add country code if missing)
            if (!phoneNumber.startsWith('+')) {
                // Add Rwanda country code if missing
                phoneNumber = phoneNumber.startsWith('0') ? 
                    '+250' + phoneNumber.substring(1) : 
                    '+250' + phoneNumber;
            }
        }
    }
    
    // Configure Flutterwave
    const config = {
        public_key: publicKey,
        tx_ref: paymentData.txRef,
        amount: paymentData.amount,
        currency: paymentData.currency,
        payment_options: paymentMethod === 'mtn' ? "mobilemoneyrw" : "card, mobilemoney, ussd",
        meta: {
            consumer_id: paymentData.customerEmail,
            consumer_mac: paymentData.txRef,
        },
        customer: {
            email: paymentData.customerEmail,
            name: paymentData.customerName,
            phone_number: phoneNumber || paymentData.customerPhone || '',
        },
        customizations: {
            title: "Signova Subscription",
            description: paymentData.description,
            logo: window.location.origin + "/static/images/signova-logo.svg",
        },
        // MTN Mobile Money specific configuration
        payment_method: paymentMethod === 'mtn' ? 'mobilemoneyrw' : '',
        callback: function(response) {
            // Handle successful payment
            if (response.status === "successful") {
                // Submit the form with the transaction details
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/payment/';
                
                // Add CSRF token
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrfmiddlewaretoken';
                csrfInput.value = csrfToken;
                form.appendChild(csrfInput);
                
                // Add plan ID
                const planInput = document.createElement('input');
                planInput.type = 'hidden';
                planInput.name = 'plan';
                planInput.value = paymentData.planId;
                form.appendChild(planInput);
                
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
                
                // Add amount
                const amountInput = document.createElement('input');
                amountInput.type = 'hidden';
                amountInput.name = 'amount';
                amountInput.value = response.amount;
                form.appendChild(amountInput);
                
                // Submit the form
                document.body.appendChild(form);
                form.submit();
            } else {
                // Handle failed payment
                resetButton(paymentData.button, 'Try Again');
                alert('Payment failed. Please try again.');
            }
        },
        onclose: function() {
            // Reset button when payment modal is closed
            resetButton(paymentData.button, paymentMethod === 'mtn' ? 'Pay with MTN MoMo' : 'Pay with Card');
            
            // Hide MTN Mobile Money instructions if they were shown
            document.querySelector('.payment-processing').style.display = 'none';
            document.querySelector('.mtn-instructions').style.display = 'none';
        }
    };
    
    // Show MTN Mobile Money instructions if applicable
    if (paymentMethod === 'mtn') {
        document.querySelector('.payment-processing').style.display = 'block';
        document.querySelector('.mtn-instructions').style.display = 'block';
        
        // Scroll to instructions
        document.querySelector('.mtn-instructions').scrollIntoView({ behavior: 'smooth' });
    }
    
    // Initialize Flutterwave checkout
    const flw = new FlutterwaveCheckout(config);
    flw.open();
}

/**
 * Reset button state
 */
function resetButton(button, text) {
    if (!button) return;
    
    button.innerHTML = text || 'Subscribe Now';
    button.disabled = false;
}

/**
 * Add Flutterwave payment to donation modal
 */
function initDonationFlutterwavePayment() {
    const donateButton = document.querySelector('#donateButton');
    
    if (!donateButton) return;
    
    donateButton.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Get donation amount
        const amountInput = document.querySelector('#donationAmount');
        const customAmountInput = document.querySelector('#customAmount');
        
        let amount = amountInput ? amountInput.value : '0';
        if (amount === 'custom' && customAmountInput) {
            amount = customAmountInput.value;
        }
        
        if (!amount || isNaN(parseFloat(amount)) || parseFloat(amount) <= 0) {
            alert('Please enter a valid donation amount');
            return;
        }
        
        // Get donation frequency
        const frequencyInput = document.querySelector('input[name="frequency"]:checked');
        const frequency = frequencyInput ? frequencyInput.value : 'one-time';
        
        // Get payment method
        const paymentMethodButton = document.querySelector('.payment-option.active');
        const paymentMethod = paymentMethodButton ? paymentMethodButton.dataset.method : 'card';
        
        // Only proceed with Flutterwave for card payments
        if (paymentMethod !== 'card') {
            alert('Please use the card payment option for online donations');
            return;
        }
        
        // Show loading state
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        this.disabled = true;
        
        // Get user details if available
        const userEmail = document.querySelector('#userEmail') ? 
                         document.querySelector('#userEmail').value : '';
        const userName = document.querySelector('#userName') ? 
                        document.querySelector('#userName').value : '';
        
        // Initialize Flutterwave checkout for donation
        makePayment({
            amount: parseFloat(amount),
            currency: 'RWF',
            description: 'Donation to Signova - ' + frequency,
            planId: 'donation',
            customerEmail: userEmail,
            customerName: userName,
            paymentPlan: frequency,
            txRef: 'signova-donation-' + generateTransactionRef(),
            button: this
        });
    });
}

// Initialize donation payment if the donation modal exists
if (document.querySelector('#donationModal')) {
    initDonationFlutterwavePayment();
}