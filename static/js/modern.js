document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    
    // Navigation functionality
    const navLinks = document.querySelectorAll('nav ul li a');
    const panels = document.querySelectorAll('.panel');
    const loadingSpinner = document.querySelector('.loading');
    const welcomeScreen = document.querySelector('.welcome-screen');
    
    // Make sure welcome screen is visible
    if (welcomeScreen) {
        welcomeScreen.style.display = 'block';
        console.log('Welcome screen should be visible');
    }
    
    // Video elements
    const videoFeed = document.getElementById('videoFeed');
    const videoPlaceholder = document.querySelector('.video-placeholder');
    const cameraToggleBtn = document.querySelector('.camera-toggle');
    const autoTranslateBtn = document.querySelector('.auto-translate');
    const translationOutput = document.querySelector('.output-text');
    
    // CTA Buttons
    const startTranslatingBtn = document.getElementById('start-translating-btn');
    const learnSignBtn = document.getElementById('learn-sign-btn');
    const aboutSignovaBtn = document.getElementById('about-signova-btn');
    
    // New UI elements
    const confidenceIndicator = document.getElementById('confidenceIndicator');
    const recognitionStatus = document.getElementById('recognitionStatus');
    const currentSign = document.getElementById('currentSign');
    const currentSentence = document.getElementById('currentSentence');
    const recentSigns = document.getElementById('recentSigns');
    const copyTextBtn = document.getElementById('copyText');
    const downloadTextBtn = document.getElementById('downloadText');
    
    let cameraActive = false;
    let autoTranslateActive = false;
    let translationInterval;
    let stream = null;
    let lastRecognizedSign = null;
    let recognitionConfidence = 0;
    
    // Direct button click handlers for CTA buttons
    if (startTranslatingBtn) {
        startTranslatingBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Start Translating button clicked');
            navigateTo('translate-panel');
        });
    }
    
    if (learnSignBtn) {
        learnSignBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Learn Sign Language button clicked');
            navigateTo('learn-panel');
        });
    }
    
    if (aboutSignovaBtn) {
        aboutSignovaBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('About Signova button clicked');
            window.location.href = '/about/';
        });
    }
    
    // Sample signs for demo
    const sampleSigns = [
        'Hello', 'Thank you', 'Please', 'Yes', 'No', 
        'Help', 'Sorry', 'Good', 'Bad', 'Love',
        'Friend', 'Family', 'Work', 'School', 'Home'
    ];
    
    // Copy text functionality
    if (copyTextBtn) {
        copyTextBtn.addEventListener('click', function() {
            const textToCopy = currentSentence.textContent;
            if (textToCopy && textToCopy !== 'No sentence yet') {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    // Show success feedback
                    const originalText = copyTextBtn.innerHTML;
                    copyTextBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                    copyTextBtn.classList.add('success');
                    
                    setTimeout(() => {
                        copyTextBtn.innerHTML = originalText;
                        copyTextBtn.classList.remove('success');
                    }, 2000);
                });
            }
        });
    }
    
    // Download text functionality
    if (downloadTextBtn) {
        downloadTextBtn.addEventListener('click', function() {
            const textToDownload = currentSentence.textContent;
            if (textToDownload && textToDownload !== 'No sentence yet') {
                const blob = new Blob([textToDownload], {type: 'text/plain'});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'signova-translation-' + new Date().toISOString().slice(0,10) + '.txt';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                
                // Show success feedback
                const originalText = downloadTextBtn.innerHTML;
                downloadTextBtn.innerHTML = '<i class="fas fa-check"></i> Downloaded!';
                downloadTextBtn.classList.add('success');
                
                setTimeout(() => {
                    downloadTextBtn.innerHTML = originalText;
                    downloadTextBtn.classList.remove('success');
                }, 2000);
            }
        });
    }
    
    // Navigation between panels
function navigateTo(panelId) {
    // Show loading spinner
    if (loadingSpinner) loadingSpinner.style.display = 'flex';
    
    // Use setTimeout to allow the browser to render the spinner before doing the heavy work
    setTimeout(() => {
        // Hide all panels
        panels.forEach(panel => {
            panel.classList.remove('active');
        });
        
        // Remove active class from all nav links
        navLinks.forEach(link => {
            link.classList.remove('active');
        });
            
            // Add active class to clicked nav link
            document.querySelector(`nav ul li a[data-panel="${panelId}"]`).classList.add('active');
            
            // Show selected panel
            document.getElementById(panelId).classList.add('active');
            
            // If navigating away from translate panel, stop camera
            if (panelId !== 'translate-panel' && cameraActive) {
                // Use SignovaUtils to stop camera
                window.SignovaUtils.stopCamera('.camera-toggle');
                cameraActive = false;
            }
            
            // Hide loading spinner after a short delay
            setTimeout(() => {
                loadingSpinner.style.display = 'none';
            }, 300);
        }, 10);
    }
    
    // Add click event to navigation links
navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const panelId = this.getAttribute('data-panel');
        if (panelId) {
            navigateTo(panelId);
        } else {
            // For links without data-panel, use the href attribute
            const href = this.getAttribute('href');
            if (href && href !== '#') {
                window.location.href = href;
            }
        }
    });
});

// Add click event to CTA buttons in welcome panel
const ctaButtons = document.querySelectorAll('.cta-buttons button');
ctaButtons.forEach(button => {
    button.addEventListener('click', function() {
        const panelId = this.getAttribute('onclick');
        if (panelId) {
            // Extract panel ID from onclick attribute (e.g., "navigateTo('translate-panel')")
            const match = panelId.match(/navigateTo\('([^']+)'\)/); 
            if (match && match[1]) {
                navigateTo(match[1]);
            }
        }
    });
});
    
    // Function to update confidence indicator
    function updateConfidenceIndicator(confidence) {
        if (!confidenceIndicator) return;
        
        // Convert confidence to percentage
        const confidencePercent = Math.round(confidence * 100);
        confidenceIndicator.textContent = confidencePercent + '%';
        
        // Update color based on confidence level
        if (confidencePercent >= 85) {
            confidenceIndicator.style.backgroundColor = 'rgba(40, 167, 69, 0.2)';
            confidenceIndicator.style.color = '#28a745';
        } else if (confidencePercent >= 70) {
            confidenceIndicator.style.backgroundColor = 'rgba(255, 193, 7, 0.2)';
            confidenceIndicator.style.color = '#ffc107';
        } else {
            confidenceIndicator.style.backgroundColor = 'rgba(220, 53, 69, 0.2)';
            confidenceIndicator.style.color = '#dc3545';
        }
    }
    
    // Function to update recent signs list
    function updateRecentSigns(sign, confidence) {
        if (!recentSigns) return;
        
        // Create new sign element
        const signElement = document.createElement('li');
        signElement.className = 'recent-sign';
        
        // Add confidence indicator
        const confidenceClass = confidence >= 0.85 ? 'high' : 
                              confidence >= 0.7 ? 'medium' : 'low';
        
        signElement.innerHTML = `
            <span class="sign-text">${sign}</span>
            <span class="sign-confidence ${confidenceClass}">${Math.round(confidence * 100)}%</span>
        `;
        
        // Add to the beginning of the list
        if (recentSigns.firstChild) {
            recentSigns.insertBefore(signElement, recentSigns.firstChild);
        } else {
            recentSigns.appendChild(signElement);
        }
        
        // Limit to 5 recent signs
        while (recentSigns.children.length > 5) {
            recentSigns.removeChild(recentSigns.lastChild);
        }
        
        // Update recognition status
        if (recognitionStatus) {
            recognitionStatus.innerHTML = '<i class="fas fa-check-circle"></i> Sign detected';
            recognitionStatus.classList.add('active');
            
            // Reset after 2 seconds
            setTimeout(() => {
                if (cameraActive) {
                    recognitionStatus.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Ready for signs';
                }
            }, 2000);
        }
    }
    
    // Camera functionality
    function toggleCamera() {
        if (cameraActive) {
            window.SignovaUtils.stopCamera('.camera-toggle');
            cameraActive = false;
        } else {
            window.SignovaUtils.startCamera('.camera-toggle');
            cameraActive = true;
        }
    }
    
    // startCamera and stopCamera functions are now handled by SignovaUtils
    // Adding event listeners for camera events
    document.addEventListener('camera-started', function() {
        // Update UI and state when camera is started by SignovaUtils
        cameraActive = true;
        if (autoTranslateBtn) autoTranslateBtn.disabled = false;
        
        // Update recognition status
        if (recognitionStatus) {
            recognitionStatus.innerHTML = '<i class="fas fa-check-circle"></i> Camera active - Ready for signs';
            recognitionStatus.classList.add('active');
        }
        
        // Update current sign display
        if (currentSign) {
            currentSign.textContent = 'Waiting for signs...';
        }
        
        // Enable copy and download buttons if sentence exists
        if (currentSentence && currentSentence.textContent !== 'No sentence yet') {
            if (copyTextBtn) copyTextBtn.disabled = false;
            if (downloadTextBtn) downloadTextBtn.disabled = false;
        }
    });
    
    document.addEventListener('camera-stopped', function() {
        // Update UI and state when camera is stopped by SignovaUtils
        cameraActive = false;
        if (autoTranslateBtn) autoTranslateBtn.disabled = true;
        
        // Update recognition status
        if (recognitionStatus) {
            recognitionStatus.innerHTML = '<i class="fas fa-pause-circle"></i> Camera stopped';
            recognitionStatus.classList.remove('active');
        }
        
        if (autoTranslateActive) {
            toggleAutoTranslate();
        }
    });
                // Error handling is now handled by SignovaUtils
    
    // stopCamera function is now handled by SignovaUtils
    
    function toggleAutoTranslate() {
        if (!cameraActive) return;
        
        if (autoTranslateActive) {
            // Stop auto-translation
            clearInterval(translationInterval);
            autoTranslateBtn.textContent = 'Start Auto-Translate';
            autoTranslateBtn.classList.remove('active');
            autoTranslateActive = false;
            translationOutput.textContent = 'Auto-translation stopped.';
        } else {
            // Start auto-translation
            autoTranslateBtn.textContent = 'Stop Auto-Translate';
            autoTranslateBtn.classList.add('active');
            autoTranslateActive = true;
            translationOutput.textContent = 'Detecting signs...';
            
            // Simulate sign detection at intervals
            let currentSentence = [];
            translationInterval = setInterval(() => {
                // Randomly select a sign from sample signs
                const randomSign = sampleSigns[Math.floor(Math.random() * sampleSigns.length)];
                
                // Add to current sentence (max 5 words)
                currentSentence.push(randomSign);
                if (currentSentence.length > 5) {
                    currentSentence.shift();
                }
                
                // Update translation output
                translationOutput.textContent = currentSentence.join(' ');
            }, 3000);
        }
    }
    
    // Text to Sign Language functionality
    const textInput = document.getElementById('textInput');
    const showSignBtn = document.getElementById('showSignBtn');
    
    function showSignLanguage() {
        const text = textInput.value.trim();
        if (!text) {
            alert('Please enter some text to translate.');
            return;
        }
        
        // Demo: Show a message for specific words
        const words = text.toLowerCase().split(/\s+/);
        let translatedWords = [];
        
        words.forEach(word => {
            // Check if word is in our sample signs
            if (sampleSigns.map(s => s.toLowerCase()).includes(word)) {
                translatedWords.push(`[Sign for "${word.toUpperCase()}"]`);
            } else {
                translatedWords.push(`[Unknown sign for "${word}"]`);
            }
        });
        
        translationOutput.innerHTML = translatedWords.join(' ');
    }
    
    // Sign Library for Learn section
    const signLibrary = [
        { name: 'Hello', video: 'hello.gif', description: 'Wave your hand with palm facing outward.' },
        { name: 'Thank You', video: 'thank-you.gif', description: 'Touch your lips with fingertips, then extend hand forward.' },
        { name: 'Please', video: 'please.gif', description: 'Rub your chest in a circular motion with an open palm.' },
        { name: 'Yes', video: 'yes.gif', description: 'Make a fist and nod it up and down, like nodding your head.' },
        { name: 'No', video: 'no.gif', description: 'Make a fist and shake it side to side, like shaking your head.' },
        { name: 'Help', video: 'help.gif', description: 'Place one hand on top of the other, then raise both hands up.' },
        { name: 'Love', video: 'love.gif', description: 'Cross your arms over your chest, like hugging yourself.' },
        { name: 'Friend', video: 'friend.gif', description: 'Hook your index fingers together, then reverse the motion.' },
        { name: 'Family', video: 'family.gif', description: 'Join both hands in a circle motion.' }
    ];
    
    function displaySigns(signs) {
        const signsGrid = document.querySelector('.signs-grid');
        signsGrid.innerHTML = '';
        
        if (signs.length === 0) {
            signsGrid.innerHTML = '<p>No signs found matching your search.</p>';
            return;
        }
        
        signs.forEach(sign => {
            // Map sign names to Giphy IDs (for demo purposes)
            const giphyId = sign.name.toLowerCase().replace(/\s+/g, '');
            const signCard = document.createElement('div');
            signCard.className = 'sign-card';
            signCard.innerHTML = `
                <img src="https://media.giphy.com/media/placeholder/${giphyId}/giphy.gif" class="sign-video" alt="${sign.name} sign">
                <div class="sign-info">
                    <h3>${sign.name}</h3>
                    <p>${sign.description}</p>
                </div>
            `;
            signsGrid.appendChild(signCard);
        });
    }
    
    // Search functionality
    const searchInput = document.querySelector('.search-box input');
    
    function searchSigns() {
        const searchTerm = searchInput.value.toLowerCase();
        if (!searchTerm) {
            displaySigns(signLibrary);
            return;
        }
        
        const filteredSigns = signLibrary.filter(sign => {
            return sign.name.toLowerCase().includes(searchTerm) || 
                   sign.description.toLowerCase().includes(searchTerm);
        });
        
        displaySigns(filteredSigns);
    }
    
    // Initialize event listeners
    if (cameraToggleBtn) {
        cameraToggleBtn.addEventListener('click', toggleCamera);
    }
    
    if (autoTranslateBtn) {
        autoTranslateBtn.addEventListener('click', toggleAutoTranslate);
    }
    
    if (showSignBtn) {
        showSignBtn.addEventListener('click', showSignLanguage);
    }
    
    if (searchInput) {
        searchInput.addEventListener('input', searchSigns);
        // Initialize sign display
        displaySigns(signLibrary);
    }
    
    // Stop camera when page is hidden
    document.addEventListener('visibilitychange', function() {
        if (document.hidden && cameraActive) {
            stopCamera();
        }
    });
    
    // Initialize with welcome panel active
    document.getElementById('welcome-panel').classList.add('active');
    document.querySelector('nav ul li a[data-panel="welcome-panel"]').classList.add('active');
});