// ==================== ADVANCED AI CHATBOT FUNCTIONALITY ====================

document.addEventListener('DOMContentLoaded', function() {
    const chatIcon = document.getElementById('chatbotIcon');
    const chatWindow = document.getElementById('chatbotWindow');
    const closeChat = document.getElementById('closeChat');
    const chatInput = document.getElementById('chatInput');
    const sendChat = document.getElementById('sendChat');
    const chatMessages = document.getElementById('chatMessages');
    
    // Generate session ID
    let sessionId = localStorage.getItem('chatSessionId');
    if (!sessionId) {
        sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('chatSessionId', sessionId);
    }
    
    // Toggle chat window with animation
    if (chatIcon) {
        chatIcon.addEventListener('click', function() {
            chatWindow.classList.toggle('active');
            if (chatWindow.classList.contains('active')) {
                chatInput.focus();
                // Play a subtle notification sound (optional)
                playNotificationSound();
            }
        });
    }
    
    if (closeChat) {
        closeChat.addEventListener('click', function() {
            chatWindow.classList.remove('active');
        });
    }
    
    // Typing indicator functions
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        chatMessages.appendChild(typingDiv);
        scrollToBottom();
    }
    
    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    // Smooth scroll to bottom
    function scrollToBottom() {
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }
    
    // Add timestamp to messages
    function formatTimestamp() {
        const now = new Date();
        return now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    }
    
    // Create message element with timestamp
    function createMessageElement(text, isUser = false) {
        const messageWrapper = document.createElement('div');
        messageWrapper.className = 'message-wrapper';
        
        const messageDiv = document.createElement('div');
        messageDiv.className = isUser ? 'user-message' : 'bot-message';
        
        // Support markdown-style formatting
        const formattedText = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
        
        messageDiv.innerHTML = formattedText;
        
        const timestamp = document.createElement('div');
        timestamp.className = 'message-timestamp';
        timestamp.textContent = formatTimestamp();
        
        messageWrapper.appendChild(messageDiv);
        messageWrapper.appendChild(timestamp);
        
        return messageWrapper;
    }
    
    // Create quick reply buttons
    function createQuickReplies(replies) {
        // Remove existing quick replies
        const existingReplies = document.querySelector('.quick-replies-container');
        if (existingReplies) {
            existingReplies.remove();
        }
        
        if (!replies || replies.length === 0) return;
        
        const container = document.createElement('div');
        container.className = 'quick-replies-container';
        
        replies.forEach(reply => {
            const button = document.createElement('button');
            button.className = 'quick-reply-btn';
            button.textContent = reply;
            button.onclick = function() {
                chatInput.value = reply;
                sendMessage();
            };
            container.appendChild(button);
        });
        
        chatMessages.appendChild(container);
        scrollToBottom();
    }
    
    // Create product cards
    function createProductCards(products) {
        if (!products || products.length === 0) return;
        
        const container = document.createElement('div');
        container.className = 'product-cards-container';
        
        products.forEach(product => {
            const card = document.createElement('div');
            card.className = 'chat-product-card';
            card.innerHTML = `
                <div class="chat-product-name">${product.name}</div>
                <div class="chat-product-price">₹${product.price}</div>
                <div class="chat-product-stock">${product.quantity > 0 ? '✅ In Stock' : '❌ Out of Stock'}</div>
            `;
            card.onclick = function() {
                window.location.href = '/products/' + product.id + '/';
            };
            container.appendChild(card);
        });
        
        chatMessages.appendChild(container);
        scrollToBottom();
    }
    
    // Play notification sound (subtle)
    function playNotificationSound() {
        // Create a subtle beep sound using Web Audio API
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = 800;
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.1);
        } catch (e) {
            // Silently fail if audio is not supported
        }
    }
    
    // Send message function with advanced features
    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;
        
        // Display user message with timestamp
        const userMessage = createMessageElement(message, true);
        chatMessages.appendChild(userMessage);
        
        // Clear input
        chatInput.value = '';
        
        // Scroll to bottom
        scrollToBottom();
        
        // Show typing indicator
        showTypingIndicator();
        
        // Simulate network delay for more realistic feel
        const minDelay = 500;
        const maxDelay = 1500;
        const delay = Math.random() * (maxDelay - minDelay) + minDelay;
        
        // Send to backend
        fetch('/api/chatbot/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        })
        .then(response => response.json())
        .then(data => {
            setTimeout(() => {
                hideTypingIndicator();
                
                // Display bot response with typing effect
                const botMessage = createMessageElement(data.response, false);
                chatMessages.appendChild(botMessage);
                
                // Play notification sound
                playNotificationSound();
                
                // Show quick replies if available
                if (data.quick_replies && data.quick_replies.length > 0) {
                    createQuickReplies(data.quick_replies);
                }
                
                // Show product cards if available
                if (data.products && data.products.length > 0) {
                    createProductCards(data.products);
                }
                
                // Scroll to bottom
                scrollToBottom();
            }, delay);
        })
        .catch(error => {
            hideTypingIndicator();
            console.error('Error:', error);
            
            const errorMessage = createMessageElement(
                '😔 Oops! Something went wrong. Please try again or refresh the page.',
                false
            );
            chatMessages.appendChild(errorMessage);
            scrollToBottom();
        });
    }
    
    // Send on button click
    if (sendChat) {
        sendChat.addEventListener('click', sendMessage);
    }
    
    // Send on Enter key
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    // Add initial greeting with animation
    if (chatWindow) {
        setTimeout(() => {
            const greetingMessage = createMessageElement(
                "👋 Hi! I'm your AI shopping assistant powered by advanced algorithms. Ask me anything!",
                false
            );
            const initialGreeting = chatMessages.querySelector('.bot-message');
            if (initialGreeting && initialGreeting.textContent === "Hi! How can I help you today?") {
                initialGreeting.parentElement.remove();
            }
            // chatMessages.appendChild(greetingMessage);
        }, 500);
    }
});

// ==================== AUTO-HIDE MESSAGES ====================

document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.alert');
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 300);
        }, 5000);
    });
});

// ==================== CART QUANTITY UPDATE ====================

document.addEventListener('DOMContentLoaded', function() {
    const quantityInputs = document.querySelectorAll('.item-quantity input[type="number"]');
    quantityInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            if (this.value < 1) {
                this.value = 1;
            }
        });
    });
});

// ==================== CONFIRM DELETE ====================

document.addEventListener('DOMContentLoaded', function() {
    const deleteForms = document.querySelectorAll('form[name="delete_product"]');
    deleteForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });
});

// ==================== MOBILE MENU TOGGLE ====================

document.addEventListener('DOMContentLoaded', function() {
    // Add mobile menu toggle if needed
    const navLinks = document.querySelector('.nav-links');
    if (window.innerWidth <= 768 && navLinks) {
        const menuToggle = document.createElement('button');
        menuToggle.className = 'menu-toggle';
        menuToggle.innerHTML = '☰';
        menuToggle.style.cssText = 'background: none; border: none; color: white; font-size: 1.5rem; cursor: pointer; display: block;';
        
        const navbar = document.querySelector('.navbar .container');
        navbar.insertBefore(menuToggle, navLinks);
        
        menuToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }
});

// ==================== FORM VALIDATION ====================

document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = '#dc2626';
                } else {
                    field.style.borderColor = '#d1d5db';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
});

// ==================== SMOOTH SCROLL ====================

document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
});

// ==================== IMAGE PREVIEW ====================

document.addEventListener('DOMContentLoaded', function() {
    const imageInputs = document.querySelectorAll('input[type="file"]');
    imageInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    // Create preview (you can customize this based on your needs)
                    console.log('Image selected:', event.target.result);
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
});

// ==================== LOADING INDICATOR ====================

function showLoading() {
    const loader = document.createElement('div');
    loader.id = 'loading-indicator';
    loader.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    `;
    loader.innerHTML = '<div style="font-size: 2rem; color: #2563eb;">Loading...</div>';
    document.body.appendChild(loader);
}

function hideLoading() {
    const loader = document.getElementById('loading-indicator');
    if (loader) {
        loader.remove();
    }
}

// ==================== AJAX FORM SUBMISSIONS ====================

document.addEventListener('DOMContentLoaded', function() {
    // You can add AJAX form handling here if needed
    const ajaxForms = document.querySelectorAll('.ajax-form');
    ajaxForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            showLoading();
            
            const formData = new FormData(this);
            const url = this.action;
            
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                hideLoading();
                if (data.success) {
                    location.reload();
                } else {
                    alert(data.message || 'An error occurred');
                }
            })
            .catch(error => {
                hideLoading();
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            });
        });
    });
});

// ==================== UTILITIES ====================

// Format currency
function formatCurrency(amount) {
    return '₹' + parseFloat(amount).toFixed(2);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions if needed
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
window.debounce = debounce;
