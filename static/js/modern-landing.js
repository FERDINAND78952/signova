/**
 * Modern Landing Page JavaScript
 * This file contains all the interactive functionality for the Signova landing page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initNavigation();
    initScrollAnimations();
    initReadMore();
    initTestimonialSlider();
    initMoreStories();
    initFlashcards();
    initDailyChallenge();
    initVideoTutorials();
    initModals();
    initTranslator();
    initSignLibrary();
    initAuthForms();
    initDonationForm();
    initChatbot();
});

/**
 * Navigation functionality
 */
function initNavigation() {
    const header = document.getElementById('main-header');
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mainNav = document.getElementById('main-nav');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Sticky header on scroll
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
    
    // Mobile menu toggle
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenuToggle.classList.toggle('active');
            mainNav.classList.toggle('active');
        });
    }
    
    // Smooth scroll for navigation links
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            
            // Only process if it's an anchor link
            if (targetId.startsWith('#') && targetId.length > 1) {
                e.preventDefault();
                
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    // Close mobile menu if open
                    if (mainNav.classList.contains('active')) {
                        mainNav.classList.remove('active');
                        mobileMenuToggle.classList.remove('active');
                    }
                    
                    // Smooth scroll to target
                    window.scrollTo({
                        top: targetElement.offsetTop - 80, // Adjust for header height
                        behavior: 'smooth'
                    });
                    
                    // Update active link
                    navLinks.forEach(navLink => navLink.classList.remove('active'));
                    this.classList.add('active');
                }
            }
        });
    });
    
    // Update active link on scroll
    window.addEventListener('scroll', function() {
        let current = '';
        const sections = document.querySelectorAll('section[id]');
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100;
            const sectionHeight = section.offsetHeight;
            
            if (window.scrollY >= sectionTop && window.scrollY < sectionTop + sectionHeight) {
                current = '#' + section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === current) {
                link.classList.add('active');
            }
        });
    });
}

/**
 * Scroll animations
 */
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.animate-fade-in, .animate-slide-up, .animate-slide-left, .animate-slide-right');
    
    // Initial check for elements in viewport
    checkAnimations();
    
    // Check on scroll
    window.addEventListener('scroll', checkAnimations);
    
    function checkAnimations() {
        animatedElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementVisible = 150;
            
            if (elementTop < window.innerHeight - elementVisible) {
                element.style.visibility = 'visible';
            }
        });
    }
}

/**
 * Read More functionality
 */
function initReadMore() {
    const readMoreBtn = document.getElementById('read-more-btn');
    const sectionContent = document.querySelector('.section-content');
    
    if (readMoreBtn && sectionContent) {
        readMoreBtn.addEventListener('click', function() {
            sectionContent.classList.toggle('expanded');
        });
    }
}

/**
 * Testimonial Slider
 */
function initTestimonialSlider() {
    const track = document.querySelector('.testimonial-track');
    const slides = document.querySelectorAll('.testimonial');
    const dotsContainer = document.querySelector('.slider-dots');
    const prevBtn = document.querySelector('.slider-arrow.prev');
    const nextBtn = document.querySelector('.slider-arrow.next');
    
    if (!track || slides.length === 0) return;
    
    let currentIndex = 0;
    
    // Create dots
    if (dotsContainer) {
        slides.forEach((_, index) => {
            const dot = document.createElement('div');
            dot.classList.add('slider-dot');
            if (index === 0) dot.classList.add('active');
            dot.addEventListener('click', () => goToSlide(index));
            dotsContainer.appendChild(dot);
        });
    }
    
    // Add event listeners to buttons
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            currentIndex = (currentIndex - 1 + slides.length) % slides.length;
            updateSlider();
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            currentIndex = (currentIndex + 1) % slides.length;
            updateSlider();
        });
    }
    
    // Go to specific slide
    function goToSlide(index) {
        currentIndex = index;
        updateSlider();
    }
    
    // Update slider position and active dot
    function updateSlider() {
        track.style.transform = `translateX(-${currentIndex * 100}%)`;
        
        // Update dots
        const dots = document.querySelectorAll('.slider-dot');
        dots.forEach((dot, index) => {
            if (index === currentIndex) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }
    
    // Auto play slider
    let interval = setInterval(() => {
        currentIndex = (currentIndex + 1) % slides.length;
        updateSlider();
    }, 5000);
    
    // Pause auto play on hover
    track.addEventListener('mouseenter', () => clearInterval(interval));
    track.addEventListener('mouseleave', () => {
        interval = setInterval(() => {
            currentIndex = (currentIndex + 1) % slides.length;
            updateSlider();
        }, 5000);
    });
    
    // Handle audio play buttons
    const audioPlayBtns = document.querySelectorAll('.audio-play-btn');
    audioPlayBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const testimonialText = this.closest('.testimonial').querySelector('.testimonial-content p').textContent;
            speakText(testimonialText);
        });
    });
}

/**
 * More Stories functionality
 */
function initMoreStories() {
    const moreStoriesBtn = document.getElementById('more-stories-btn');
    const additionalStories = document.querySelector('.additional-stories');
    
    if (moreStoriesBtn && additionalStories) {
        moreStoriesBtn.addEventListener('click', function() {
            additionalStories.classList.toggle('expanded');
            
            if (additionalStories.classList.contains('expanded')) {
                this.textContent = 'Show Less Stories';
            } else {
                this.textContent = 'Show More Stories';
            }
        });
    }
}

/**
 * Flashcards functionality
 */
function initFlashcards() {
    const flashcards = document.querySelectorAll('.flashcard');
    
    flashcards.forEach(card => {
        card.addEventListener('click', function() {
            this.querySelector('.flashcard-inner').style.transform = 
                this.querySelector('.flashcard-inner').style.transform === 'rotateY(180deg)' ? 
                'rotateY(0deg)' : 'rotateY(180deg)';
        });
    });
}

/**
 * Daily Challenge functionality
 */
function initDailyChallenge() {
    const challengeBtn = document.getElementById('challenge-btn');
    const challengeResult = document.querySelector('.challenge-result');
    const challengeVideo = document.getElementById('challenge-video');
    
    if (challengeBtn && challengeResult && challengeVideo) {
        challengeBtn.addEventListener('click', function() {
            // Simulate loading
            showLoading();
            
            setTimeout(() => {
                hideLoading();
                challengeResult.classList.add('active');
                challengeVideo.play();
            }, 1500);
        });
    }
}

/**
 * Video Tutorials functionality
 */
function initVideoTutorials() {
    const playlistItems = document.querySelectorAll('.playlist-item');
    const tutorialVideo = document.getElementById('tutorial-video');
    
    if (playlistItems.length > 0 && tutorialVideo) {
        playlistItems.forEach(item => {
            item.addEventListener('click', function() {
                // Remove active class from all items
                playlistItems.forEach(i => i.classList.remove('active'));
                
                // Add active class to clicked item
                this.classList.add('active');
                
                // Update video source (in a real app, this would be a real video source)
                const videoSrc = this.getAttribute('data-video-src');
                if (videoSrc) {
                    tutorialVideo.src = videoSrc;
                    tutorialVideo.play();
                }
            });
        });
    }
}

/**
 * Modal functionality
 */
function initModals() {
    const modalTriggers = document.querySelectorAll('[data-modal]');
    const modals = document.querySelectorAll('.modal');
    const closeButtons = document.querySelectorAll('.modal-close');
    
    // Open modal
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal');
            const modal = document.getElementById(modalId);
            
            if (modal) {
                modal.classList.add('active');
                document.body.style.overflow = 'hidden'; // Prevent scrolling
            }
        });
    });
    
    // Close modal with close button
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            closeModal(modal);
        });
    });
    
    // Close modal when clicking outside content
    modals.forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal(this);
            }
        });
    });
    
    // Close modal with ESC key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal.active');
            if (activeModal) {
                closeModal(activeModal);
            }
        }
    });
    
    function closeModal(modal) {
        modal.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
        
        // Stop videos if any
        const videos = modal.querySelectorAll('video');
        videos.forEach(video => {
            video.pause();
            video.currentTime = 0;
        });
    }
}

/**
 * Sign Translator functionality
 */
function initTranslator() {
    const startCameraBtn = document.getElementById('start-camera-btn');
    const stopCameraBtn = document.getElementById('stop-camera-btn');
    const translatorVideo = document.getElementById('translator-video');
    const videoPlaceholder = document.querySelector('.video-placeholder');
    const translateBtn = document.getElementById('translate-btn');
    const textInput = document.getElementById('text-input');
    const resultsContainer = document.querySelector('.results-container');
    const confidenceLevel = document.querySelector('.confidence-level');
    const confidencePercentage = document.querySelector('.confidence-percentage');
    const speakBtn = document.getElementById('speak-btn');
    
    let stream = null;
    
    // Start camera
    if (startCameraBtn && translatorVideo) {
        startCameraBtn.addEventListener('click', async function() {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ video: true });
                translatorVideo.srcObject = stream;
                translatorVideo.play();
                
                if (videoPlaceholder) videoPlaceholder.style.display = 'none';
                startCameraBtn.disabled = true;
                if (stopCameraBtn) stopCameraBtn.disabled = false;
                
                // Simulate sign detection after a delay
                setTimeout(simulateSignDetection, 3000);
            } catch (err) {
                console.error('Error accessing camera:', err);
                alert('Could not access camera. Please make sure you have granted camera permissions.');
            }
        });
    }
    
    // Stop camera
    if (stopCameraBtn) {
        stopCameraBtn.addEventListener('click', function() {
            if (stream) {
                const tracks = stream.getTracks();
                tracks.forEach(track => track.stop());
                translatorVideo.srcObject = null;
                
                if (videoPlaceholder) videoPlaceholder.style.display = 'flex';
                startCameraBtn.disabled = false;
                stopCameraBtn.disabled = true;
            }
        });
    }
    
    // Simulate sign detection
    function simulateSignDetection() {
        if (!stream) return;
        
        showLoading();
        
        setTimeout(() => {
            hideLoading();
            
            // Sample signs to detect randomly
            const signs = ['Hello', 'Thank you', 'How are you?', 'Good', 'Help', 'Please'];
            const randomSign = signs[Math.floor(Math.random() * signs.length)];
            
            if (resultsContainer) {
                resultsContainer.innerHTML = `<p class="typing-text">Detected Sign: ${randomSign}</p>`;
            }
            
            // Update confidence meter
            const randomConfidence = Math.floor(Math.random() * 30) + 70; // Between 70-99%
            if (confidenceLevel) confidenceLevel.style.width = `${randomConfidence}%`;
            if (confidencePercentage) confidencePercentage.textContent = `${randomConfidence}%`;
            
            // Continue detection if camera is still on
            if (stream && stream.active) {
                setTimeout(simulateSignDetection, 5000);
            }
        }, 1500);
    }
    
    // Text to sign translation
    if (translateBtn && textInput) {
        translateBtn.addEventListener('click', function() {
            const text = textInput.value.trim();
            if (text) {
                showLoading();
                
                setTimeout(() => {
                    hideLoading();
                    
                    if (resultsContainer) {
                        resultsContainer.innerHTML = `<p class="typing-text">Text converted to sign language: "${text}"</p>`;
                    }
                    
                    // Update confidence meter
                    const randomConfidence = Math.floor(Math.random() * 20) + 80; // Between 80-99%
                    if (confidenceLevel) confidenceLevel.style.width = `${randomConfidence}%`;
                    if (confidencePercentage) confidencePercentage.textContent = `${randomConfidence}%`;
                }, 1500);
            }
        });
    }
    
    // Text to speech
    if (speakBtn) {
        speakBtn.addEventListener('click', function() {
            const text = resultsContainer ? resultsContainer.textContent.trim() : '';
            if (text) {
                speakText(text);
            }
        });
    }
}

/**
 * Sign Library functionality
 */
function initSignLibrary() {
    const librarySearchInput = document.getElementById('library-search-input');
    const librarySearchBtn = document.getElementById('library-search-btn');
    const categoryBtns = document.querySelectorAll('.category-btn');
    const libraryGrid = document.querySelector('.library-grid');
    const prevPageBtn = document.getElementById('prev-page-btn');
    const nextPageBtn = document.getElementById('next-page-btn');
    const paginationInfo = document.querySelector('.pagination-info');
    
    // Sample sign data
    const signData = [
        { name: 'Hello', category: 'Greetings', videoSrc: '/videos/Hello.mp4' },
        { name: 'Thank You', category: 'Greetings', videoSrc: '/videos/ThankYou.mp4' },
        { name: 'How Are You', category: 'Questions', videoSrc: '/videos/HowAreYou.mp4' },
        { name: 'My Name Is', category: 'Introduction', videoSrc: '/videos/MyNameIs.mp4' },
        { name: 'I Want', category: 'Common', videoSrc: '/videos/Iwant.mp4' },
        { name: 'You', category: 'Pronouns', videoSrc: '/videos/You.mp4' },
        { name: 'Remember', category: 'Actions', videoSrc: '/videos/Remember.mp4' },
        { name: 'Forget', category: 'Actions', videoSrc: '/videos/Forget.mp4' },
        { name: 'Same To You', category: 'Responses', videoSrc: '/videos/SameToYou.mp4' },
        // Add more sample signs as needed
    ];
    
    let currentPage = 1;
    const itemsPerPage = 8;
    let filteredSigns = [...signData];
    
    // Initial render
    renderLibrary();
    
    // Search functionality
    if (librarySearchBtn && librarySearchInput) {
        librarySearchBtn.addEventListener('click', function() {
            const searchTerm = librarySearchInput.value.trim().toLowerCase();
            
            if (searchTerm) {
                filteredSigns = signData.filter(sign => 
                    sign.name.toLowerCase().includes(searchTerm) || 
                    sign.category.toLowerCase().includes(searchTerm)
                );
            } else {
                filteredSigns = [...signData];
            }
            
            currentPage = 1;
            renderLibrary();
        });
        
        // Search on Enter key
        librarySearchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                librarySearchBtn.click();
            }
        });
    }
    
    // Category filter
    if (categoryBtns.length > 0) {
        categoryBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                // Toggle active state
                categoryBtns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                const category = this.getAttribute('data-category');
                
                if (category === 'all') {
                    filteredSigns = [...signData];
                } else {
                    filteredSigns = signData.filter(sign => sign.category === category);
                }
                
                currentPage = 1;
                renderLibrary();
            });
        });
    }
    
    // Pagination
    if (prevPageBtn) {
        prevPageBtn.addEventListener('click', function() {
            if (currentPage > 1) {
                currentPage--;
                renderLibrary();
            }
        });
    }
    
    if (nextPageBtn) {
        nextPageBtn.addEventListener('click', function() {
            const totalPages = Math.ceil(filteredSigns.length / itemsPerPage);
            if (currentPage < totalPages) {
                currentPage++;
                renderLibrary();
            }
        });
    }
    
    // Render library grid
    function renderLibrary() {
        if (!libraryGrid) return;
        
        // Calculate pagination
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        const currentSigns = filteredSigns.slice(startIndex, endIndex);
        const totalPages = Math.ceil(filteredSigns.length / itemsPerPage);
        
        // Update pagination buttons and info
        if (prevPageBtn) prevPageBtn.disabled = currentPage === 1;
        if (nextPageBtn) nextPageBtn.disabled = currentPage === totalPages;
        if (paginationInfo) {
            paginationInfo.textContent = `Page ${currentPage} of ${totalPages || 1}`;
        }
        
        // Clear grid
        libraryGrid.innerHTML = '';
        
        // Add sign cards
        currentSigns.forEach(sign => {
            const card = document.createElement('div');
            card.classList.add('sign-card');
            card.innerHTML = `
                <div class="sign-video-container">
                    <video class="sign-video" src="${sign.videoSrc}" loop muted></video>
                </div>
                <div class="sign-info">
                    <div class="sign-name">${sign.name}</div>
                    <div class="sign-category">${sign.category}</div>
                </div>
            `;
            
            // Play video on hover
            const video = card.querySelector('video');
            card.addEventListener('mouseenter', () => video.play());
            card.addEventListener('mouseleave', () => {
                video.pause();
                video.currentTime = 0;
            });
            
            // Show in modal on click
            card.addEventListener('click', function() {
                // In a real app, this would open a detailed view of the sign
                alert(`Sign details: ${sign.name} (${sign.category})`);
            });
            
            libraryGrid.appendChild(card);
        });
        
        // Show message if no results
        if (currentSigns.length === 0) {
            libraryGrid.innerHTML = '<p>No signs found matching your search criteria.</p>';
        }
    }
}

/**
 * Authentication Forms functionality
 */
function initAuthForms() {
    const authTabs = document.querySelectorAll('.auth-tab');
    const authForms = document.querySelectorAll('.auth-form');
    
    if (authTabs.length > 0 && authForms.length > 0) {
        authTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const formId = this.getAttribute('data-form');
                
                // Update active tab
                authTabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                
                // Show selected form
                authForms.forEach(form => {
                    form.classList.remove('active');
                    if (form.id === formId) {
                        form.classList.add('active');
                    }
                });
            });
        });
    }
    
    // Form validation
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Simple validation
            const email = this.querySelector('input[type="email"]').value;
            const password = this.querySelector('input[type="password"]').value;
            
            if (email && password) {
                showLoading();
                
                // Simulate API call
                setTimeout(() => {
                    hideLoading();
                    alert('Login successful! (This is a demo)');
                    
                    // Close modal
                    const modal = this.closest('.modal');
                    if (modal) modal.classList.remove('active');
                }, 1500);
            }
        });
    }
    
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Simple validation
            const name = this.querySelector('input[name="name"]').value;
            const email = this.querySelector('input[type="email"]').value;
            const password = this.querySelector('input[type="password"]').value;
            
            if (name && email && password) {
                showLoading();
                
                // Simulate API call
                setTimeout(() => {
                    hideLoading();
                    alert('Account created successfully! (This is a demo)');
                    
                    // Close modal
                    const modal = this.closest('.modal');
                    if (modal) modal.classList.remove('active');
                }, 1500);
            }
        });
    }
}

/**
 * Donation Form functionality
 */
function initDonationForm() {
    const donationAmounts = document.querySelectorAll('.donation-amount');
    const customAmountContainer = document.querySelector('.custom-amount-container');
    const customAmountOption = document.querySelector('.donation-amount[data-amount="custom"]');
    const donationForm = document.getElementById('donation-form');
    
    // Select donation amount
    if (donationAmounts.length > 0) {
        donationAmounts.forEach(amount => {
            amount.addEventListener('click', function() {
                // Update active state
                donationAmounts.forEach(a => a.classList.remove('active'));
                this.classList.add('active');
                
                // Show/hide custom amount input
                if (customAmountContainer) {
                    if (this === customAmountOption) {
                        customAmountContainer.classList.add('active');
                    } else {
                        customAmountContainer.classList.remove('active');
                    }
                }
            });
        });
    }
    
    // Form submission
    if (donationForm) {
        donationForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            showLoading();
            
            // Simulate API call
            setTimeout(() => {
                hideLoading();
                alert('Thank you for your donation! (This is a demo)');
                
                // Close modal
                const modal = this.closest('.modal');
                if (modal) modal.classList.remove('active');
            }, 1500);
        });
    }
}

/**
 * Chatbot functionality
 */
function initChatbot() {
    const chatbotBubble = document.querySelector('.chatbot-bubble');
    const chatbotContainer = document.querySelector('.chatbot-container');
    const chatbotClose = document.querySelector('.chatbot-close');
    const chatbotMessages = document.querySelector('.chatbot-messages');
    const chatbotInput = document.getElementById('chatbot-message-input');
    const chatbotSendBtn = document.getElementById('chatbot-send-btn');
    
    // Sample responses
    const botResponses = [
        "Hello! How can I help you with sign language today?",
        "Signova helps bridge communication gaps through AI-powered sign language translation.",
        "Our sign language translator can recognize over 1,000 signs across multiple sign languages.",
        "You can learn sign language through our interactive tutorials and daily challenges.",
        "The mobile app will be available next month for both iOS and Android.",
        "Sign language varies by country and region, just like spoken languages.",
        "Our technology uses computer vision and machine learning to recognize hand gestures and facial expressions.",
        "You can book a demo by visiting the 'Contact Us' section of our website."
    ];
    
    // Toggle chatbot
    if (chatbotBubble && chatbotContainer) {
        chatbotBubble.addEventListener('click', function() {
            chatbotContainer.classList.add('active');
            chatbotBubble.style.display = 'none';
            
            // Add welcome message if empty
            if (chatbotMessages && chatbotMessages.children.length === 0) {
                addBotMessage("Hi there! 👋 I'm Siggy, your Signova assistant. How can I help you today?");
            }
        });
    }
    
    // Close chatbot
    if (chatbotClose) {
        chatbotClose.addEventListener('click', function() {
            chatbotContainer.classList.remove('active');
            chatbotBubble.style.display = 'flex';
        });
    }
    
    // Send message
    function sendMessage() {
        if (!chatbotInput || !chatbotMessages) return;
        
        const message = chatbotInput.value.trim();
        if (message) {
            // Add user message
            addUserMessage(message);
            chatbotInput.value = '';
            
            // Show typing indicator
            showTypingIndicator();
            
            // Simulate bot response after delay
            setTimeout(() => {
                hideTypingIndicator();
                
                // Get random response or smart response based on keywords
                let response = getBotResponse(message);
                addBotMessage(response);
                
                // Scroll to bottom
                chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
            }, 1500);
        }
    }
    
    // Send on button click
    if (chatbotSendBtn) {
        chatbotSendBtn.addEventListener('click', sendMessage);
    }
    
    // Send on Enter key
    if (chatbotInput) {
        chatbotInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
    
    // Add user message to chat
    function addUserMessage(text) {
        if (!chatbotMessages) return;
        
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'user-message');
        messageElement.textContent = text;
        chatbotMessages.appendChild(messageElement);
        
        // Scroll to bottom
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }
    
    // Add bot message to chat
    function addBotMessage(text) {
        if (!chatbotMessages) return;
        
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'bot-message');
        messageElement.textContent = text;
        chatbotMessages.appendChild(messageElement);
        
        // Scroll to bottom
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }
    
    // Show typing indicator
    function showTypingIndicator() {
        if (!chatbotMessages) return;
        
        const typingIndicator = document.createElement('div');
        typingIndicator.classList.add('typing-indicator');
        typingIndicator.innerHTML = `
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        `;
        typingIndicator.id = 'typing-indicator';
        chatbotMessages.appendChild(typingIndicator);
        
        // Scroll to bottom
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }
    
    // Hide typing indicator
    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    // Get bot response based on user message
    function getBotResponse(message) {
        message = message.toLowerCase();
        
        // Check for specific keywords
        if (message.includes('hello') || message.includes('hi') || message.includes('hey')) {
            return "Hello! How can I help you with sign language today?";
        } else if (message.includes('how does') || message.includes('work')) {
            return "Signova uses advanced AI and computer vision to recognize sign language gestures and translate them into text or speech in real-time.";
        } else if (message.includes('cost') || message.includes('price') || message.includes('subscription')) {
            return "We offer a free basic plan and premium subscriptions starting at $9.99/month with additional features like offline mode and expanded sign libraries.";
        } else if (message.includes('learn') || message.includes('tutorial')) {
            return "Our Learning Hub offers interactive tutorials, daily challenges, and video lessons for all skill levels. You can access it by clicking 'Learning Hub' in the navigation.";
        } else if (message.includes('thank')) {
            return "You're welcome! Is there anything else I can help you with?";
        } else {
            // Return random response if no keywords match
            return botResponses[Math.floor(Math.random() * botResponses.length)];
        }
    }
}

/**
 * Utility Functions
 */

// Text to speech function
function speakText(text) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        window.speechSynthesis.speak(utterance);
    } else {
        console.error('Text-to-speech not supported in this browser');
    }
}

// Show loading spinner
function showLoading() {
    let loadingContainer = document.querySelector('.loading-container');
    
    if (!loadingContainer) {
        loadingContainer = document.createElement('div');
        loadingContainer.classList.add('loading-container');
        loadingContainer.innerHTML = `
            <div class="loading-spinner"></div>
            <p class="loading-text">Processing...</p>
        `;
        document.body.appendChild(loadingContainer);
    }
    
    loadingContainer.classList.add('active');
}

// Hide loading spinner
function hideLoading() {
    const loadingContainer = document.querySelector('.loading-container');
    if (loadingContainer) {
        loadingContainer.classList.remove('active');
    }
}