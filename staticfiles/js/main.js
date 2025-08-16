// Main JavaScript for Signova Web Application

document.addEventListener('DOMContentLoaded', function() {
    // Feature buttons functionality
    const featureButtons = document.querySelectorAll('.feature-button');
    
    featureButtons.forEach(button => {
        button.addEventListener('click', function() {
            const buttonText = this.textContent.trim();
            
            switch(buttonText) {
                case 'Camera':
                    window.location.href = '/translate';
                    break;
                case 'Audio':
                    // Audio translation functionality will be implemented in future
                    alert('Audio translation coming soon!');
                    break;
                case 'Type':
                    // Text input translation functionality will be implemented in future
                    alert('Text translation coming soon!');
                    break;
                default:
                    break;
            }
        });
    });
    
    // Mobile menu toggle (for responsive design)
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (mobileMenuToggle && navMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
    
    // Language selection functionality
    const languageItems = document.querySelectorAll('.language-list li');
    
    languageItems.forEach(item => {
        item.addEventListener('click', function() {
            // This will be expanded when language selection is implemented
            const language = this.textContent.trim();
            console.log(`Selected language: ${language}`);
        });
    });
});

// Translation page specific functionality
if (window.location.pathname.includes('/translate')) {
    let cameraActive = false;
    
    // Start camera button
    const startCameraBtn = document.getElementById('start-camera');
    if (startCameraBtn) {
        startCameraBtn.addEventListener('click', function() {
            if (!cameraActive) {
                fetch('/start_camera')
                    .then(response => response.json())
                    .then(data => {
                        console.log(data.status);
                        cameraActive = true;
                        this.textContent = 'Stop Camera';
                        document.getElementById('video-feed').style.display = 'block';
                        // Start polling for recognized signs
                        startSignPolling();
                    })
                    .catch(error => console.error('Error starting camera:', error));
            } else {
                fetch('/stop_camera')
                    .then(response => response.json())
                    .then(data => {
                        console.log(data.status);
                        cameraActive = false;
                        this.textContent = 'Start Camera';
                        document.getElementById('video-feed').style.display = 'none';
                        // Stop polling
                        stopSignPolling();
                    })
                    .catch(error => console.error('Error stopping camera:', error));
            }
        });
    }
    
    // Clear sentence button
    const clearSentenceBtn = document.getElementById('clear-sentence');
    if (clearSentenceBtn) {
        clearSentenceBtn.addEventListener('click', function() {
            fetch('/clear_sentence')
                .then(response => response.json())
                .then(data => {
                    console.log(data.status);
                    document.getElementById('current-sentence').textContent = '';
                })
                .catch(error => console.error('Error clearing sentence:', error));
        });
    }
    
    // Speak sentence button
    const speakSentenceBtn = document.getElementById('speak-sentence');
    if (speakSentenceBtn) {
        speakSentenceBtn.addEventListener('click', function() {
            fetch('/speak_sentence')
                .then(response => response.json())
                .then(data => console.log(data.status))
                .catch(error => console.error('Error speaking sentence:', error));
        });
    }
    
    let signPollingInterval;
    
    function startSignPolling() {
        // Poll for recognized signs every 500ms
        signPollingInterval = setInterval(() => {
            fetch('/get_recognized_signs')
                .then(response => response.json())
                .then(data => {
                    // Update the recognized signs display
                    const signsContainer = document.getElementById('recognized-signs');
                    if (signsContainer) {
                        signsContainer.innerHTML = '';
                        data.signs.forEach(sign => {
                            const signElement = document.createElement('span');
                            signElement.classList.add('sign');
                            signElement.textContent = sign;
                            signsContainer.appendChild(signElement);
                        });
                    }
                    
                    // Update the current sentence display
                    const sentenceElement = document.getElementById('current-sentence');
                    if (sentenceElement) {
                        sentenceElement.textContent = data.current_sentence;
                    }
                })
                .catch(error => console.error('Error getting recognized signs:', error));
        }, 500);
    }
    
    function stopSignPolling() {
        clearInterval(signPollingInterval);
    }
}

// Learn page specific functionality
if (window.location.pathname.includes('/learn')) {
    const videoLinks = document.querySelectorAll('.video-link');
    const videoPlayer = document.getElementById('video-player');
    
    if (videoLinks && videoPlayer) {
        videoLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const videoName = this.getAttribute('data-video');
                videoPlayer.src = `/video/${videoName}`;
                
                // Update active class
                videoLinks.forEach(vl => vl.classList.remove('active'));
                this.classList.add('active');
                
                // Update video title
                const videoTitle = document.getElementById('video-title');
                if (videoTitle) {
                    videoTitle.textContent = this.textContent.trim();
                }
            });
        });
    }
}