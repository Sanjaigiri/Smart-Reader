// Article Reading Page JavaScript - Extracted for Performance
// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// Initialize from page data
let articleId, articleContent, startTime, lastSaveTime, selectedColor;
let initialTimeFromDb, maxProgressReached, totalTimeOnPage, pageStartTime, lastDisplayUpdate;
let scrollTimeout;

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    articleId = document.getElementById('articleId').value;
    articleContent = document.getElementById('articleContent');
    startTime = Date.now();
    lastSaveTime = Date.now();
    selectedColor = 'yellow';
    
    // Get progress values
    initialTimeFromDb = parseInt(document.getElementById('articleContent').dataset.initialTime) || 0;
    maxProgressReached = parseInt(document.getElementById('maxProgress').value) || 0;
    
    // Track total time on page
    totalTimeOnPage = initialTimeFromDb;
    pageStartTime = Date.now();
    lastDisplayUpdate = Date.now();
    
    // Scroll to last position
    const lastPos = parseInt(document.getElementById('lastPosition').value) || 0;
    if (lastPos > 0) {
        window.scrollTo(0, lastPos);
    }
    
    // Update display with max progress
    updateProgressDisplay(maxProgressReached);
    
    // Style the last paragraph as conclusion
    styleConclusionParagraph();
    
    // Set up event listeners
    setupEventListeners();
    
    // Start time tracking
    setInterval(updateTimeDisplay, 1000);
    setInterval(saveProgress, 60000);
    setInterval(() => {
        const timeActive = Math.floor((Date.now() - lastSaveTime) / 1000);
        if (timeActive >= 30) {
            saveProgress();
        }
    }, 30000);
});

// Notification System
function showNotification(title, message, type = 'info', actions = null) {
    const backdrop = document.getElementById('notificationBackdrop');
    const modal = document.getElementById('notificationModal');
    const icon = document.getElementById('notificationIcon');
    const titleEl = document.getElementById('notificationTitle');
    const messageEl = document.getElementById('notificationMessage');
    const actionsContainer = document.getElementById('notificationActions');
    
    titleEl.textContent = title;
    messageEl.textContent = message;
    
    icon.className = 'notification-icon ' + type;
    const iconMap = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    icon.innerHTML = `<i class="${iconMap[type] || iconMap.info}"></i>`;
    
    if (actions && Array.isArray(actions)) {
        actionsContainer.innerHTML = actions.map(action => 
            `<button class="${action.class || 'btn-primary'}" onclick="${action.onclick || 'closeNotification()'}">${action.text}</button>`
        ).join('');
    } else {
        actionsContainer.innerHTML = '<button class="btn-primary" onclick="closeNotification()">OK</button>';
    }
    
    backdrop.classList.add('active');
    modal.classList.add('show');
    modal.style.display = 'block';
}

function closeNotification() {
    const backdrop = document.getElementById('notificationBackdrop');
    const modal = document.getElementById('notificationModal');
    backdrop.classList.remove('active');
    modal.classList.remove('show');
    modal.style.display = 'none';
}

function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `notification-toast ${type}`;
    toast.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : type === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// Style conclusion paragraph
function styleConclusionParagraph() {
    const articleContent = document.getElementById('articleContent');
    if (!articleContent) return;
    
    const paragraphs = articleContent.querySelectorAll('p');
    if (paragraphs.length === 0) return;
    
    let lastParagraph = null;
    for (let i = paragraphs.length - 1; i >= 0; i--) {
        const text = paragraphs[i].textContent.trim();
        if (text.length > 20) {
            lastParagraph = paragraphs[i];
            break;
        }
    }
    
    if (lastParagraph) {
        lastParagraph.classList.add('conclusion-paragraph');
    }
}

// Update progress display
function updateProgressDisplay(percentage) {
    const sidebarProgress = document.getElementById('sidebarProgress');
    const progressPercent = document.getElementById('progressPercent');
    if (sidebarProgress) sidebarProgress.style.width = percentage + '%';
    if (progressPercent) progressPercent.textContent = percentage + '%';
}

// Check if user has reached conclusion
function hasReachedConclusion() {
    const conclusionEl = document.querySelector('.conclusion-paragraph');
    if (!conclusionEl) return false;
    
    const conclusionRect = conclusionEl.getBoundingClientRect();
    const windowHeight = window.innerHeight;
    
    return conclusionRect.top <= windowHeight && conclusionRect.bottom >= 0;
}

// Update reading progress
function updateProgress() {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    
    let currentPercentage;
    if (scrollTop + 10 >= docHeight) {
        currentPercentage = 100;
    } else {
        currentPercentage = Math.min(100, Math.round((scrollTop / docHeight) * 100));
    }
    
    document.getElementById('progressBar').style.width = currentPercentage + '%';
    
    if (currentPercentage > maxProgressReached) {
        maxProgressReached = currentPercentage;
        updateProgressDisplay(maxProgressReached);
    }
    
    if (hasReachedConclusion() && maxProgressReached < 100) {
        maxProgressReached = 100;
        updateProgressDisplay(100);
    }
    
    return { scrollTop, currentPercentage, maxPercentage: maxProgressReached };
}

// Update time display
function updateTimeDisplay() {
    const currentSessionTime = Math.floor((Date.now() - pageStartTime) / 1000);
    const displayTime = Math.floor(initialTimeFromDb) + currentSessionTime;
    const timeSpentEl = document.getElementById('timeSpent');
    if (timeSpentEl) {
        timeSpentEl.textContent = displayTime;
    }
}

// Save progress
function saveProgress() {
    const { scrollTop, currentPercentage, maxPercentage } = updateProgress();
    const currentTime = Date.now();
    const timeSpent = Math.floor((currentTime - lastSaveTime) / 1000);
    
    if (timeSpent < 2) return;
    
    totalTimeOnPage = initialTimeFromDb + Math.floor((Date.now() - pageStartTime) / 1000);
    
    fetch('/save-progress/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            article_id: articleId,
            position: scrollTop,
            percentage: currentPercentage,
            time: timeSpent
        })
    })
    .then(response => response.json())
    .then(data => {
        lastSaveTime = Date.now();
        if (data.max_percentage) {
            maxProgressReached = Math.max(maxProgressReached, data.max_percentage);
            updateProgressDisplay(maxProgressReached);
        }
        if (data.total_time) {
            totalTimeOnPage = data.total_time;
        }
        if (data.just_completed) {
            showCompletionNotification(data);
        }
    })
    .catch(err => console.error('Error saving progress:', err));
}

// Show completion notification
function showCompletionNotification(data) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 2rem 3rem;
        border-radius: 16px;
        box-shadow: 0 20px 60px rgba(16, 185, 129, 0.4);
        z-index: 10000;
        text-align: center;
        animation: slideInScale 0.5s ease-out;
    `;
    
    const goalMessage = data.weekly_goal_achieved 
        ? `<p style="font-size: 1.125rem; margin-top: 0.5rem;">🎉 Weekly goal achieved! (${data.this_week_reads}/${data.reading_goal})</p>`
        : `<p style="font-size: 1.125rem; margin-top: 0.5rem;">Progress: ${data.this_week_reads}/${data.reading_goal} articles this week</p>`;
    
    notification.innerHTML = `
        <h2 style="font-size: 2rem; margin-bottom: 0.5rem;">✨ Article Completed! ✨</h2>
        ${goalMessage}
        <p style="font-size: 0.9rem; opacity: 0.9; margin-top: 1rem;">Great job! Keep reading!</p>
    `;
    
    document.body.appendChild(notification);
    createConfetti();
    
    setTimeout(() => {
        notification.style.animation = 'slideOutScale 0.5s ease-in';
        setTimeout(() => notification.remove(), 500);
    }, 4000);
}

// Create confetti effect
function createConfetti() {
    const colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff'];
    for (let i = 0; i < 50; i++) {
        const confetti = document.createElement('div');
        confetti.style.cssText = `
            position: fixed;
            width: 10px;
            height: 10px;
            background: ${colors[Math.floor(Math.random() * colors.length)]};
            top: 50%;
            left: 50%;
            opacity: 1;
            pointer-events: none;
            z-index: 9999;
            animation: confettiFall ${1 + Math.random() * 2}s linear forwards;
        `;
        confetti.style.setProperty('--x', (Math.random() - 0.5) * 200 + 'vw');
        confetti.style.setProperty('--y', Math.random() * 100 + 'vh');
        document.body.appendChild(confetti);
        setTimeout(() => confetti.remove(), 3000);
    }
}

// Highlight selection
function highlightSelection(color) {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        const text = selection.toString();
        
        const mark = document.createElement('mark');
        mark.className = 'highlight-' + color;
        range.surroundContents(mark);
        
        fetch('/save-highlight/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                article_id: articleId,
                text: text,
                color: color
            })
        });
        
        const selectionPopup = document.getElementById('selectionPopup');
        selectionPopup.classList.remove('active');
        selection.removeAllRanges();
        showToast('Highlight saved successfully!', 'success', 2000);
    }
}

// Add note from selection
function addNoteFromSelection() {
    const selection = window.getSelection();
    const text = selection.toString().trim();
    
    if (text) {
        document.getElementById('selectedTextInput').value = text;
        document.querySelector('.note-form textarea').focus();
    }
    
    document.getElementById('selectionPopup').classList.remove('active');
}

// Bookmark toggle
function toggleBookmark() {
    fetch('/toggle-bookmark/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ article_id: articleId })
    })
    .then(response => response.json())
    .then(data => {
        const btn = document.getElementById('bookmarkBtn');
        if (data.status === 'added') {
            btn.classList.remove('btn-secondary');
            btn.classList.add('btn-primary');
            btn.innerHTML = '<i class="fas fa-bookmark"></i> Bookmarked';
            showToast('Article bookmarked!', 'success', 2000);
        } else {
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-secondary');
            btn.innerHTML = '<i class="far fa-bookmark"></i> Bookmark';
            showToast('Bookmark removed!', 'info', 2000);
        }
    });
}

// Rate article
function rateArticle(score) {
    const emojiMap = {
        1: { emoji: '😞', message: 'We\'re sorry! We\'ll try to improve.' },
        2: { emoji: '😕', message: 'Thanks for the feedback! We can do better.' },
        3: { emoji: '😊', message: 'Good! Thanks for reading.' },
        4: { emoji: '😄', message: 'Great! We\'re glad you enjoyed it!' },
        5: { emoji: '🤩', message: 'Awesome! You\'re amazing! Thanks for the 5 stars!' }
    };
    
    document.querySelectorAll('.star-rating i[data-article-rating]').forEach((star, index) => {
        if (index < score) {
            star.classList.remove('far');
            star.classList.add('fas');
            star.style.color = '#fbbf24';
            star.style.textShadow = '0 0 5px rgba(251, 191, 36, 0.5)';
        } else {
            star.classList.remove('fas');
            star.classList.add('far');
            star.style.color = 'inherit';
            star.style.textShadow = 'none';
        }
    });
    
    const emoji = emojiMap[score];
    document.getElementById('ratingEmoji').textContent = emoji.emoji;
    document.getElementById('ratingMessage').textContent = emoji.message;
    
    fetch('/rate-article/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            article_id: articleId,
            score: score
        })
    })
    .then(response => response.json())
    .then(data => {
        document.querySelector('.avg-rating').textContent = data.avg_rating;
    });
}

// Submit feedback
function submitFeedback(event) {
    event.preventDefault();
    const feedbackText = document.getElementById('feedbackText').value;
    
    fetch('/submit-feedback/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            article_id: articleId,
            feedback_text: feedbackText,
            is_helpful: true
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification('Thank You!', 'Your feedback has been submitted successfully.', 'success', [
                { text: 'Close', onclick: 'closeNotificationAndClear()', class: 'btn-primary' }
            ]);
        } else {
            showNotification('Error', 'Failed to submit feedback. Please try again.', 'error');
        }
    })
    .catch(err => {
        showNotification('Error', 'Network error. Please try again.', 'error');
    });
}

function closeNotificationAndClear() {
    closeNotification();
    document.getElementById('feedbackText').value = '';
}

// Share article
function shareArticle() {
    if (navigator.share) {
        navigator.share({
            title: document.querySelector('.article-title').textContent,
            url: window.location.href
        });
    } else {
        navigator.clipboard.writeText(window.location.href);
        showToast('Link copied to clipboard!', 'success', 2000);
    }
}

// Toggle purchase dropdown
function togglePurchaseDropdown(event) {
    event.stopPropagation();
    const dropdown = document.getElementById('purchaseDropdown');
    dropdown.classList.toggle('show');
}

// Set up event listeners
function setupEventListeners() {
    // Scroll handler
    window.addEventListener('scroll', () => {
        updateProgress();
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(saveProgress, 1000);
    });
    
    // Selection popup
    if (articleContent) {
        articleContent.addEventListener('mouseup', (e) => {
            const selection = window.getSelection();
            if (selection.toString().trim().length > 0) {
                const range = selection.getRangeAt(0);
                const rect = range.getBoundingClientRect();
                
                const selectionPopup = document.getElementById('selectionPopup');
                selectionPopup.style.top = (rect.top + window.scrollY - 50) + 'px';
                selectionPopup.style.left = (rect.left + rect.width / 2 - 80) + 'px';
                selectionPopup.classList.add('active');
            } else {
                const selectionPopup = document.getElementById('selectionPopup');
                selectionPopup.classList.remove('active');
            }
        });
    }
    
    // Global click handler
    document.addEventListener('click', function(event) {
        const dropdown = document.getElementById('purchaseDropdown');
        if (dropdown && !event.target.closest('.dropdown-wrapper')) {
            dropdown.classList.remove('show');
        }
        
        const ratingStar = event.target.closest('[data-article-rating]');
        if (ratingStar) {
            const rating = parseInt(ratingStar.getAttribute('data-rating'));
            rateArticle(rating);
        }
    });
    
    // Notification backdrop click
    const backdrop = document.getElementById('notificationBackdrop');
    if (backdrop) {
        backdrop.addEventListener('click', closeNotification);
    }
    
    // Save progress before leaving
    window.addEventListener('beforeunload', saveProgress);
}
