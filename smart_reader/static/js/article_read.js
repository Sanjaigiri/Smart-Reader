// Article Reading Page JavaScript - Extracted for Performance
// Use CSRF token from base template (already defined globally)

// Initialize from page data
let articleId, articleContent, startTime, lastSaveTime, selectedColor;
let initialTimeFromDb, maxProgressReached, totalTimeOnPage, pageStartTime, lastDisplayUpdate;
let scrollTimeout, progressSaveInFlight, savedSelectionRange;

function getProgressStorageKey() {
    return articleId ? `smartreader-progress-${articleId}` : null;
}

function readLocalProgress() {
    const key = getProgressStorageKey();
    if (!key) return null;

    try {
        const raw = localStorage.getItem(key);
        return raw ? JSON.parse(raw) : null;
    } catch (error) {
        console.error('Failed to read local progress:', error);
        return null;
    }
}

function writeLocalProgress(progress) {
    const key = getProgressStorageKey();
    if (!key) return;

    try {
        localStorage.setItem(key, JSON.stringify(progress));
    } catch (error) {
        console.error('Failed to write local progress:', error);
    }
}

// Restore saved highlights on page load
function restoreSavedHighlights() {
    if (typeof window.savedHighlights === 'undefined' || !window.savedHighlights || !articleContent) {
        return;
    }
    
    const highlights = window.savedHighlights;
    console.log('SmartReader: Restoring', highlights.length, 'saved highlights');
    
    highlights.forEach(function(highlight) {
        const text = highlight.text;
        const color = highlight.color || 'yellow';
        
        if (!text || text.trim().length === 0) return;
        
        // Use TreeWalker to find the text in the article content
        const walker = document.createTreeWalker(
            articleContent,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        let node;
        let found = false;
        
        while ((node = walker.nextNode()) && !found) {
            const nodeText = node.textContent;
            const index = nodeText.indexOf(text);
            
            if (index !== -1) {
                try {
                    const range = document.createRange();
                    range.setStart(node, index);
                    range.setEnd(node, index + text.length);
                    
                    const mark = document.createElement('mark');
                    mark.className = 'highlight-' + color;
                    mark.style.cursor = 'pointer';
                    range.surroundContents(mark);
                    found = true;
                } catch (e) {
                    console.warn('Could not restore highlight:', text.substring(0, 30) + '...');
                }
            }
        }
    });
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log('SmartReader: Initializing article reader...');
    
    // Get article ID first
    const articleIdEl = document.getElementById('articleId');
    if (!articleIdEl) {
        console.error('Article ID element not found');
        return;
    }
    articleId = articleIdEl.value;
    articleContent = document.getElementById('articleContent');
    startTime = Date.now();
    lastSaveTime = Date.now();
    selectedColor = 'yellow';
    
    // Get progress values - initialTimeFromDb is set as global var in template
    initialTimeFromDb = typeof window.initialTimeFromDb !== 'undefined' ? Number(window.initialTimeFromDb) : 0;
    
    // Check if article is already completed
    const isCompletedEl = document.getElementById('isCompleted');
    const isAlreadyCompleted = isCompletedEl && isCompletedEl.value === 'true';
    
    const maxProgressEl = document.getElementById('maxProgress');
    maxProgressReached = maxProgressEl ? parseInt(maxProgressEl.value) || 0 : 0;
    
    // If already completed, ensure it stays at 100%
    if (isAlreadyCompleted) {
        maxProgressReached = 100;
    }
    
    const localProgress = readLocalProgress();
    if (localProgress && !isAlreadyCompleted) {
        initialTimeFromDb = Math.max(initialTimeFromDb, Number(localProgress.timeSpent) || 0);
        maxProgressReached = Math.max(maxProgressReached, Number(localProgress.maxProgress) || 0);
    }
    
    // Track total time on page
    totalTimeOnPage = initialTimeFromDb;
    pageStartTime = Date.now();
    lastDisplayUpdate = Date.now();
    progressSaveInFlight = false;
    savedSelectionRange = null;
    
    // Restore saved highlights
    restoreSavedHighlights();
    
    // Scroll to last position
    const lastPosEl = document.getElementById('lastPosition');
    const lastPos = lastPosEl ? parseInt(lastPosEl.value) || 0 : 0;
    if (lastPos > 0) {
        window.scrollTo(0, lastPos);
    }
    
    // Update display immediately
    updateProgress();
    updateTimeDisplay();
    
    // Style the last paragraph as conclusion
    styleConclusionParagraph();
    
    // Set up event listeners
    setupEventListeners();
    
    // Start time tracking - update every second
    setInterval(function() {
        updateTimeDisplay();
        updateProgress(); // Also update progress every second for real-time display
    }, 1000);
    
    // Auto-save progress every 30 seconds
    setInterval(function() {
        saveProgress();
    }, 30000);
    
    // Save progress when user leaves the page (using sendBeacon for reliability)
    window.addEventListener('beforeunload', function() {
        saveProgressOnUnload();
    });
    
    // Also save on visibility change (when tab is hidden)
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'hidden') {
            saveProgressOnUnload();
        }
    });
    
    console.log('SmartReader: Initialized! Time:', initialTimeFromDb, 'Progress:', maxProgressReached + '%');
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

// Toast notification matching Django messages style
function showToast(message, type = 'info', duration = 2500) {
    // Remove existing toast if any
    const existing = document.querySelector('.toast-message');
    if (existing) existing.remove();
    
    const toast = document.createElement('div');
    toast.className = 'toast-message';
    // Standardize message wording for highlights
    let displayMsg = message;
    if (message.toLowerCase().includes('rating saved')) {
        displayMsg = 'Rating saved successfully!';
    } else if (message.toLowerCase().includes('highlight saved')) {
        displayMsg = 'Highlight saved successfully!';
    }
    toast.innerHTML = `<i class="fas fa-check-circle" style="color:#10b981;font-size:18px;"></i><span>${displayMsg}</span>`;
    toast.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        background: white;
        border: 1px solid #e5e7eb;
        border-left: 4px solid #10b981;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 14px;
        color: #333;
        z-index: 10001;
        animation: toastSlideIn 0.3s ease;
    `;
    
    // Add animation keyframes if not exists
    if (!document.getElementById('toastAnimStyle')) {
        const style = document.createElement('style');
        style.id = 'toastAnimStyle';
        style.textContent = `
            @keyframes toastSlideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), duration);
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
    if (docHeight <= 0) {
        currentPercentage = 100;
    } else if (scrollTop + 10 >= docHeight) {
        currentPercentage = 100;
    } else {
        currentPercentage = Math.min(100, Math.round((scrollTop / docHeight) * 100));
    }
    
    // Update top progress bar with current position
    const progressBar = document.getElementById('progressBar');
    if (progressBar) {
        progressBar.style.width = currentPercentage + '%';
    }
    
    // Update max progress reached (for saving) - progress only increases, never decreases
    if (currentPercentage > maxProgressReached) {
        maxProgressReached = currentPercentage;
    }
    
    if (hasReachedConclusion() && maxProgressReached < 100) {
        maxProgressReached = 100;
    }
    
    // Always show max progress reached in sidebar (never decrease)
    updateProgressDisplay(maxProgressReached);

    writeLocalProgress({
        maxProgress: maxProgressReached,
        timeSpent: initialTimeFromDb + Math.floor((Date.now() - pageStartTime) / 1000),
        lastPosition: scrollTop
    });
    
    return { scrollTop, currentPercentage, maxPercentage: maxProgressReached };
}

// Format seconds as readable time string
function formatTime(totalSeconds) {
    totalSeconds = Math.floor(totalSeconds);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${seconds}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${seconds}s`;
    } else {
        return `${seconds}s`;
    }
}

// Update time display
function updateTimeDisplay() {
    const currentSessionTime = Math.floor((Date.now() - pageStartTime) / 1000);
    const displayTime = Math.floor(initialTimeFromDb) + currentSessionTime;
    const timeSpentEl = document.getElementById('timeSpent');
    if (timeSpentEl) {
        timeSpentEl.textContent = formatTime(displayTime);
    }
    // Also update sidebar progress to make sure it's in sync
    updateProgressDisplay(maxProgressReached);
    writeLocalProgress({
        maxProgress: maxProgressReached,
        timeSpent: displayTime,
        lastPosition: window.scrollY || 0
    });
}

// Update progress display
function updateProgressDisplay(percentage) {
    const sidebarProgress = document.getElementById('sidebarProgress');
    const progressPercent = document.getElementById('progressPercent');
    if (sidebarProgress) {
        sidebarProgress.style.width = percentage + '%';
    }
    if (progressPercent) {
        progressPercent.textContent = percentage + '%';
    }
}

// Save progress
function saveProgress() {
    if (!articleId || progressSaveInFlight) return;

    const { scrollTop, currentPercentage, maxPercentage } = updateProgress();
    const currentTime = Date.now();
    const timeSpent = Math.floor((currentTime - lastSaveTime) / 1000);
    
    if (timeSpent < 2) return;
    
    totalTimeOnPage = initialTimeFromDb + Math.floor((Date.now() - pageStartTime) / 1000);
    
    progressSaveInFlight = true;

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
            initialTimeFromDb = data.total_time;
            pageStartTime = Date.now();
            updateTimeDisplay();
        }
        writeLocalProgress({
            maxProgress: maxProgressReached,
            timeSpent: data.total_time || totalTimeOnPage,
            lastPosition: scrollTop
        });
        if (data.just_completed) {
            showCompletionNotification(data);
        }
    })
    .catch(err => {
        console.error('Error saving progress:', err);
        writeLocalProgress({
            maxProgress: maxProgressReached,
            timeSpent: totalTimeOnPage,
            lastPosition: scrollTop
        });
    })
    .finally(() => {
        progressSaveInFlight = false;
    });
}

// Save progress on page unload using sendBeacon (works even when page is closing)
function saveProgressOnUnload() {
    if (!articleId) return;
    
    const { scrollTop, currentPercentage, maxPercentage } = updateProgress();
    const currentTime = Date.now();
    const timeSpent = Math.floor((currentTime - lastSaveTime) / 1000);
    
    // Use sendBeacon for reliable delivery on page unload
    if (navigator.sendBeacon) {
        const blob = new Blob([JSON.stringify({
            article_id: articleId,
            position: scrollTop,
            percentage: maxPercentage, // Send max percentage to ensure completion is recorded
            time: timeSpent,
            csrfmiddlewaretoken: csrftoken  // Include CSRF token in body
        })], { type: 'application/json' });
        
        navigator.sendBeacon('/save-progress/', blob);
    } else {
        // Fallback for older browsers - synchronous XMLHttpRequest
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/save-progress/', false); // Synchronous
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.setRequestHeader('X-CSRFToken', csrftoken);
        xhr.send(JSON.stringify({
            article_id: articleId,
            position: scrollTop,
            percentage: maxPercentage,
            time: timeSpent
        }));
    }
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
function getActiveSelectionRange() {
    const selection = window.getSelection();
    
    // First, try current selection
    if (selection && selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        const text = selection.toString().trim();
        if (text && articleContent && articleContent.contains(range.commonAncestorContainer)) {
            savedSelectionRange = range.cloneRange();
            return savedSelectionRange;
        }
    }
    
    // Fall back to saved selection
    if (savedSelectionRange) {
        try {
            const text = savedSelectionRange.toString().trim();
            if (text) {
                return savedSelectionRange;
            }
        } catch (e) {
            savedSelectionRange = null;
        }
    }
    
    return null;
}

function applyHighlightToRange(range, color) {
    if (!range) return false;
    
    const mark = document.createElement('mark');
    mark.className = 'highlight-' + color;
    mark.style.cursor = 'pointer';

    try {
        // Clone the range to avoid modifying the original
        const workingRange = range.cloneRange();
        workingRange.surroundContents(mark);
        return true;
    } catch (error) {
        try {
            const workingRange = range.cloneRange();
            const fragment = workingRange.extractContents();
            mark.appendChild(fragment);
            workingRange.insertNode(mark);
            return true;
        } catch (fallbackError) {
            console.error('Error applying highlight:', fallbackError);
            return false;
        }
    }
}

function highlightSelection(color) {
    let range = getActiveSelectionRange();
    if (!range) {
        showToast('Select some text first', 'warning');
        return;
    }

    // Expand selection to full words
    let text = range.toString();
    if (!text.trim()) {
        showToast('Select some text first', 'warning');
        return;
    }

    // Only expand if selection is not a full word
    const wordRegex = /^\s*\S+\s*$/;
    if (!wordRegex.test(text)) {
        // Expand left
        let startOffset = range.startOffset;
        let endOffset = range.endOffset;
        let node = range.startContainer;
        let nodeText = node.textContent;
        // Expand start
        while (startOffset > 0 && !/\s/.test(nodeText[startOffset - 1])) {
            startOffset--;
        }
        // Expand end
        while (endOffset < nodeText.length && !/\s/.test(nodeText[endOffset])) {
            endOffset++;
        }
        range.setStart(node, startOffset);
        range.setEnd(node, endOffset);
        text = range.toString();
    }

    const applied = applyHighlightToRange(range, color);
    if (!applied) {
        showToast('Could not highlight', 'error');
        return;
    }

    fetch('/save-highlight/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            article_id: articleId,
            text: text.trim(),
            color: color
        })
    })
    .then(response => response.json())
    .then(() => {
        showToast('Highlight saved!', 'success');
    })
    .catch(() => {
        showToast('Highlight applied', 'info');
    });

    const selection = window.getSelection();
    if (selection) {
        selection.removeAllRanges();
    }

    savedSelectionRange = null;
    const selectionPopup = document.getElementById('selectionPopup');
    if (selectionPopup) {
        selectionPopup.classList.remove('active');
    }
}

// Add note from selection
function addNoteFromSelection() {
    const range = getActiveSelectionRange();
    const text = range ? range.toString().trim() : '';
    
    if (text) {
        document.getElementById('selectedTextInput').value = text;
        document.querySelector('.note-form textarea').focus();
    }
    
    const selectionPopup = document.getElementById('selectionPopup');
    if (selectionPopup) {
        selectionPopup.classList.remove('active');
    }
}

// Select highlight color from sidebar
function selectHighlightColor(color, btn) {
    // Update selected color
    selectedColor = color;
    
    // Update active state on buttons
    document.querySelectorAll('.highlight-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    
    // Try to get the saved selection range
    const range = savedSelectionRange;
    const text = range ? range.toString().trim() : '';
    
    if (text && text.length > 0) {
        // Apply highlight with the selected color
        const applied = applyHighlightToRange(range, color);
        if (applied) {
            // Save to server
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
            })
            .then(response => response.json())
            .then(() => {
                showToast('Highlighted!', 'success');
            })
            .catch(() => {
                // Applied locally
            });
            
            // Clear selection
            const selection = window.getSelection();
            if (selection) {
                selection.removeAllRanges();
            }
            savedSelectionRange = null;
            
            const selectionPopup = document.getElementById('selectionPopup');
            if (selectionPopup) {
                selectionPopup.classList.remove('active');
            }
        }
    }
}

// Bookmark toggle
function toggleBookmark() {
    const btn = document.getElementById('bookmarkBtn');
    if (!btn) {
        console.error('Bookmark button not found');
        return;
    }
    
    // Ensure articleId is set
    if (!articleId) {
        const articleIdEl = document.getElementById('articleId');
        if (articleIdEl) {
            articleId = articleIdEl.value;
        }
    }
    
    if (!articleId) {
        console.error('Article ID not found');
        return;
    }
    
    // Disable button while processing
    btn.disabled = true;
    
    console.log('Toggling bookmark for article:', articleId);
    
    fetch('/toggle-bookmark/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ article_id: parseInt(articleId) })
    })
    .then(response => {
        console.log('Bookmark response status:', response.status);
        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        console.log('Bookmark response data:', data);
        if (data.status === 'added') {
            btn.classList.remove('btn-secondary');
            btn.classList.add('btn-primary');
            btn.innerHTML = '<i class="fas fa-bookmark"></i> Bookmarked';
        } else if (data.status === 'removed') {
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-secondary');
            btn.innerHTML = '<i class="far fa-bookmark"></i> Bookmark';
        }
    })
    .catch(error => {
        console.error('Bookmark error:', error);
    })
    .finally(() => {
        btn.disabled = false;
    });
}

// Preview stars on hover
function previewStars(count) {
    document.querySelectorAll('.star-rating i[data-article-rating]').forEach((star, index) => {
        if (index < count) {
            star.style.color = '#fbbf24';
            star.style.transform = 'scale(1.1)';
        } else {
            star.style.color = '#d1d5db';
            star.style.transform = 'scale(1)';
        }
    });
}

// Reset stars to default
function resetStars() {
    document.querySelectorAll('.star-rating i[data-article-rating]').forEach((star) => {
        if (!star.classList.contains('fas')) {
            star.style.color = '#d1d5db';
        }
        star.style.transform = 'scale(1)';
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
    
    const stars = document.querySelectorAll('.star-rating i[data-article-rating]');
    stars.forEach((star, index) => {
        if (index < score) {
            star.classList.remove('far');
            star.classList.add('fas');
            star.style.color = '#fbbf24';
            star.style.textShadow = '0 0 5px rgba(251, 191, 36, 0.5)';
        } else {
            star.classList.remove('fas');
            star.classList.add('far');
            star.style.color = '#d1d5db';
            star.style.textShadow = 'none';
        }
    });
    
    const emojiEl = document.getElementById('ratingEmoji');
    const messageEl = document.getElementById('ratingMessage');
    
    if (emojiEl && emojiMap[score]) {
        emojiEl.textContent = emojiMap[score].emoji;
        messageEl.textContent = emojiMap[score].message;
    }
    
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
        const avgRatingEl = document.querySelector('.avg-rating');
        if (avgRatingEl && data.avg_rating) {
            avgRatingEl.textContent = data.avg_rating;
        }
        showToast('Rating saved!', 'success');
    })
    .catch(err => {
        showToast('Rating failed', 'error');
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
            showToast('Feedback saved successfully!', 'success');
            closeNotificationAndClear();
        } else {
            showToast('Failed to submit feedback. Please try again.', 'error');
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
        showToast('Link copied!', 'success');
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
    // Scroll handler - use passive for performance, update immediately
    let lastScrollTime = 0;
    window.addEventListener('scroll', () => {
        const now = Date.now();
        // Update display on every scroll for real-time feedback
        updateProgress();
        updateTimeDisplay();
        
        // Debounce save to reduce server calls
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(saveProgress, 1000);
    }, { passive: true });
    
    // Also update on any user interaction
    document.addEventListener('click', updateProgress);
    
    // Selection popup
    if (articleContent) {
        articleContent.addEventListener('mouseup', function(e) {
            // Small delay to ensure selection is complete
            setTimeout(updateSelectionPopup, 10);
        });
        articleContent.addEventListener('keyup', updateSelectionPopup);
        
        // Track selection more aggressively
        articleContent.addEventListener('mousedown', function() {
            // Clear old selection on new mousedown
            savedSelectionRange = null;
        });
    }

    document.addEventListener('selectionchange', () => {
        const selection = window.getSelection();
        if (!selection || selection.rangeCount === 0) return;

        const text = selection.toString().trim();
        const range = selection.getRangeAt(0);
        if (text && articleContent && articleContent.contains(range.commonAncestorContainer)) {
            savedSelectionRange = range.cloneRange();
        }
    });
    
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
            // Update stored rating after clicking
            window.currentArticleRating = rating;
        }
    });
    
    // Star rating hover preview
    const starRatingContainer = document.querySelector('.star-rating');
    if (starRatingContainer) {
        // Get any existing rating
        window.currentArticleRating = 0;
        document.querySelectorAll('.star-rating i.fas[data-article-rating]').forEach((star, index) => {
            window.currentArticleRating = index + 1;
        });
        
        starRatingContainer.addEventListener('mouseover', function(e) {
            const star = e.target.closest('[data-article-rating]');
            if (star) {
                const hoverRating = parseInt(star.getAttribute('data-rating'));
                previewStars(hoverRating);
            }
        });
        
        starRatingContainer.addEventListener('mouseout', function() {
            // Restore current rating
            if (window.currentArticleRating > 0) {
                previewStars(window.currentArticleRating);
            } else {
                resetStars();
            }
        });
    }
    
    // Notification backdrop click
    const backdrop = document.getElementById('notificationBackdrop');
    if (backdrop) {
        backdrop.addEventListener('click', closeNotification);
    }
    
    // Save progress before leaving
    window.addEventListener('beforeunload', saveProgress);
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'hidden') {
            saveProgress();
        }
    });
}

function updateSelectionPopup() {
    const selectionPopup = document.getElementById('selectionPopup');
    if (!selectionPopup) return;

    const range = getActiveSelectionRange();
    if (!range || !range.toString().trim()) {
        selectionPopup.classList.remove('active');
        return;
    }

    const rect = range.getBoundingClientRect();
    if (!rect || (!rect.width && !rect.height)) {
        selectionPopup.classList.remove('active');
        return;
    }

    selectionPopup.style.top = (rect.top + window.scrollY - 50) + 'px';
    selectionPopup.style.left = (rect.left + rect.width / 2 - 80) + 'px';
    selectionPopup.classList.add('active');
}
