// CV Analysis Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initTabs();
    initHighlights();
    initScoreAnimation();
    initImprovementCards();
});

// Tab Functionality
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const panel = this.closest('.panel');
            const tabName = this.dataset.tab;

            // Update active button
            panel.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            // Update active content
            panel.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });

            const targetTab = panel.querySelector(`#${tabName}-tab`);
            if (targetTab) {
                targetTab.classList.add('active');
            }
        });
    });
}

// Highlight Interactions
function initHighlights() {
    const highlights = document.querySelectorAll('[class*="highlight-"]');
    const tooltip = document.getElementById('highlightTooltip');

    highlights.forEach(highlight => {
        if (!highlight.dataset.suggestion) return;

        highlight.addEventListener('mouseenter', function(e) {
            const suggestion = this.dataset.suggestion;
            tooltip.querySelector('.tooltip-content').textContent = suggestion;
            tooltip.classList.add('visible');

            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
        });

        highlight.addEventListener('mouseleave', function() {
            tooltip.classList.remove('visible');
        });
    });
}

// Animate Score Circle
function initScoreAnimation() {
    const scoreCircle = document.querySelector('.score-circle');
    if (!scoreCircle) return;

    const score = parseInt(scoreCircle.dataset.score) || 0;
    const progressCircle = scoreCircle.querySelector('.score-progress');
    const scoreNumber = scoreCircle.querySelector('.score-number');

    // Calculate stroke-dashoffset (283 is circumference of circle with r=45)
    const circumference = 283;
    const offset = circumference - (score / 100) * circumference;

    // Set color based on score
    let color = '#dc3545'; // Red for low
    if (score >= 70) color = '#28a745'; // Green for high
    else if (score >= 50) color = '#ffc107'; // Yellow for medium

    progressCircle.style.stroke = color;

    // Animate after a short delay
    setTimeout(() => {
        progressCircle.style.strokeDashoffset = offset;
        animateNumber(scoreNumber, 0, score, 1000);
    }, 300);
}

// Animate number counting
function animateNumber(element, start, end, duration) {
    const range = end - start;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing function
        const easeOutQuad = progress * (2 - progress);
        const current = Math.round(start + range * easeOutQuad);

        element.textContent = current;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

// Improvement Cards Interaction
function initImprovementCards() {
    const cards = document.querySelectorAll('.improvement-card');

    cards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Don't trigger if clicking the apply button
            if (e.target.closest('.btn-apply')) return;

            const highlightTarget = this.dataset.highlight;
            if (highlightTarget) {
                scrollToHighlight(highlightTarget);
            }
        });
    });
}

// Scroll to highlighted section in CV
function scrollToHighlight(section) {
    const cvPanel = document.querySelector('.cv-panel .panel-content');
    const highlight = document.querySelector(`[class*="highlight-"][data-section="${section}"]`);

    if (highlight && cvPanel) {
        highlight.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Flash effect
        highlight.style.transition = 'box-shadow 0.3s ease';
        highlight.style.boxShadow = '0 0 0 3px rgba(221, 98, 45, 0.5)';
        setTimeout(() => {
            highlight.style.boxShadow = '';
        }, 1500);
    }
}

// Zoom Functions
let currentZoom = 1;

function zoomIn() {
    if (currentZoom < 1.5) {
        currentZoom += 0.1;
        applyZoom();
    }
}

function zoomOut() {
    if (currentZoom > 0.7) {
        currentZoom -= 0.1;
        applyZoom();
    }
}

function applyZoom() {
    const cvDocument = document.getElementById('cvDocument');
    if (cvDocument) {
        cvDocument.style.transform = `scale(${currentZoom})`;
    }
}

// Apply Improvement
function applyImprovement(button) {
    const card = button.closest('.improvement-card');

    // Show loading state
    button.innerHTML = '<i class="bi bi-hourglass-split"></i> Applying...';
    button.disabled = true;

    // Simulate API call
    setTimeout(() => {
        button.innerHTML = '<i class="bi bi-check"></i> Applied!';
        button.style.background = '#28a745';
        card.style.opacity = '0.6';

        // Switch to optimized tab
        const optimizedBtn = document.querySelector('[data-tab="optimized"]');
        if (optimizedBtn) {
            optimizedBtn.click();
        }

        // Update score (simulate)
        updateScore(5);
    }, 1000);
}

// Update Score
function updateScore(increment) {
    const scoreCircle = document.querySelector('.score-circle');
    if (!scoreCircle) return;

    let currentScore = parseInt(scoreCircle.dataset.score) || 0;
    let newScore = Math.min(currentScore + increment, 100);

    scoreCircle.dataset.score = newScore;
    initScoreAnimation();
}

// Export Report
function exportReport() {
    // Implementation for PDF export
    alert('Generating PDF report...');
    // Could integrate with libraries like jsPDF or html2pdf
}

// Re-analyze
function reanalyze() {
    if (confirm('Re-analyze your CV with the current job description?')) {
        window.location.reload();
    }
}