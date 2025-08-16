/**
 * Signova Utilities - Camera Access and Navigation
 * This file provides utility functions for camera access and navigation
 * throughout the Signova application.
 */

// Immediately invoked function expression to avoid polluting global namespace
(function() {
    // Store camera stream globally within this scope
    let cameraStream = null;
    let isCameraActive = false;
    
    /**
     * Initialize the utility functions
     * Call this when the DOM is loaded
     */
    function initSignovaUtils() {
        // Add event listeners for any utility buttons if needed
        const landingButtons = document.querySelectorAll('.goto-landing');
        if (landingButtons) {
            landingButtons.forEach(button => {
                button.addEventListener('click', navigateToLanding);
            });
        }
        
        // Initialize camera buttons if they exist
        const cameraButtons = document.querySelectorAll('.camera-toggle');
        if (cameraButtons) {
            cameraButtons.forEach(button => {
                button.addEventListener('click', toggleCamera);
            });
        }
    }
    
    /**
     * Navigate to the landing page from anywhere in the application
     */
    function navigateToLanding() {
        // Stop camera if it's active before navigating
        if (isCameraActive) {
            stopCamera();
        }
        window.location.href = '/landing';
    }
    
    /**
     * Toggle camera on/off
     * @param {Event} event - The click event
     */
    function toggleCamera(event) {
        const button = event.target.closest('.camera-toggle');
        if (!button) return;
        
        // Prevent multiple clicks
        if (button.disabled) return;
        
        if (isCameraActive) {
            stopCamera(button);
        } else {
            startCamera(button);
        }
    }
    
    /**
     * Start the camera with proper error handling
     * @param {HTMLElement} button - The camera toggle button
     */
    function startCamera(button) {
        // Get video element - either from data attribute or default
        const videoId = button.getAttribute('data-video-target') || 'videoFeed';
        const videoElement = document.getElementById(videoId);
        if (!videoElement) {
            console.error('Video element not found:', videoId);
            showCameraError('Video element not found');
            return;
        }
        
        // Get placeholder element if it exists
        const placeholderId = button.getAttribute('data-placeholder') || 'video-placeholder';
        const placeholder = document.querySelector('.' + placeholderId) || document.getElementById(placeholderId);
        
        // Update button state
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Starting...';
        
        // Request camera access with constraints
        navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            },
            audio: false
        })
        .then(function(stream) {
            // Store stream for later use
            cameraStream = stream;
            videoElement.srcObject = stream;
            videoElement.play();
            
            // Update UI
            if (placeholder) placeholder.style.display = 'none';
            videoElement.style.display = 'block';
            button.innerHTML = '<i class="fas fa-video-slash"></i> Stop Camera';
            button.classList.add('active');
            button.disabled = false;
            
            // Enable related buttons if they exist
            const autoTranslateBtn = document.querySelector('.auto-translate');
            if (autoTranslateBtn) autoTranslateBtn.disabled = false;
            
            const speakTextBtn = document.querySelector('.speak-text');
            if (speakTextBtn) speakTextBtn.disabled = false;
            
            isCameraActive = true;
            
            // Dispatch custom event
            document.dispatchEvent(new CustomEvent('camera-started'));
            
            // Call the server-side camera start if configured
            const useServerProcessing = button.getAttribute('data-server-processing') === 'true';
            if (useServerProcessing) {
                fetch('/start_camera')
                    .then(response => response.json())
                    .then(data => console.log('Server camera started:', data))
                    .catch(err => console.error('Error starting server camera:', err));
            }
        })
        .catch(function(err) {
            console.error("Error accessing camera:", err);
            showCameraError(err.message || 'Could not access camera');
            button.innerHTML = '<i class="fas fa-video"></i> Start Camera';
            button.disabled = false;
        });
    }
    
    /**
     * Stop the camera
     * @param {HTMLElement} button - The camera toggle button
     */
    function stopCamera(button) {
        if (!cameraStream) return;
        
        // Update button state if provided
        if (button) {
            button.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Stopping...';
            button.disabled = true;
        }
        
        // Get video element
        const videoId = button ? button.getAttribute('data-video-target') || 'videoFeed' : 'videoFeed';
        const videoElement = document.getElementById(videoId);
        
        // Get placeholder element if it exists
        const placeholderId = button ? button.getAttribute('data-placeholder') || 'video-placeholder' : 'video-placeholder';
        const placeholder = document.querySelector('.' + placeholderId) || document.getElementById(placeholderId);
        
        // Stop all tracks in the stream
        cameraStream.getTracks().forEach(track => track.stop());
        if (videoElement) videoElement.srcObject = null;
        cameraStream = null;
        
        // Update UI
        if (placeholder) placeholder.style.display = 'flex';
        if (videoElement) videoElement.style.display = 'none';
        
        if (button) {
            button.innerHTML = '<i class="fas fa-video"></i> Start Camera';
            button.classList.remove('active');
            button.disabled = false;
        }
        
        // Disable related buttons if they exist
        const autoTranslateBtn = document.querySelector('.auto-translate');
        if (autoTranslateBtn) autoTranslateBtn.disabled = true;
        
        const speakTextBtn = document.querySelector('.speak-text');
        if (speakTextBtn) speakTextBtn.disabled = true;
        
        isCameraActive = false;
        
        // Dispatch custom event
        document.dispatchEvent(new CustomEvent('camera-stopped'));
        
        // Call the server-side camera stop if needed
        const useServerProcessing = button && button.getAttribute('data-server-processing') === 'true';
        if (useServerProcessing) {
            fetch('/stop_camera')
                .then(response => response.json())
                .then(data => console.log('Server camera stopped:', data))
                .catch(err => console.error('Error stopping server camera:', err));
        }
    }
    
    /**
     * Display camera error message
     * @param {string} message - Error message to display
     */
    function showCameraError(message) {
        // Find error display element or create one
        let errorElement = document.querySelector('.camera-error');
        
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'camera-error';
            errorElement.style.color = '#ff3860';
            errorElement.style.padding = '10px';
            errorElement.style.marginTop = '10px';
            errorElement.style.backgroundColor = 'rgba(255, 56, 96, 0.1)';
            errorElement.style.borderRadius = '4px';
            errorElement.style.fontSize = '14px';
            
            // Find a good place to insert the error
            const videoContainer = document.querySelector('.video-container') || 
                                   document.querySelector('.camera-container');
            if (videoContainer) {
                videoContainer.appendChild(errorElement);
            } else {
                // Fallback - insert after the camera button
                const cameraButton = document.querySelector('.camera-toggle');
                if (cameraButton && cameraButton.parentNode) {
                    cameraButton.parentNode.insertBefore(errorElement, cameraButton.nextSibling);
                }
            }
        }
        
        errorElement.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
        errorElement.style.display = 'block';
        
        // Hide error after 5 seconds
        setTimeout(() => {
            errorElement.style.display = 'none';
        }, 5000);
    }
    
    // Expose public methods
    window.SignovaUtils = {
        init: initSignovaUtils,
        navigateToLanding: navigateToLanding,
        startCamera: function(buttonSelector) {
            const button = document.querySelector(buttonSelector);
            if (button) startCamera(button);
        },
        stopCamera: function(buttonSelector) {
            const button = buttonSelector ? document.querySelector(buttonSelector) : null;
            stopCamera(button);
        },
        isCameraActive: function() {
            return isCameraActive;
        }
    };
    
    // Initialize when DOM is loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSignovaUtils);
    } else {
        initSignovaUtils();
    }
})();