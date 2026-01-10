/**
 * Upload Tracker - Single Function System
 * Manages upload quotas with backend persistence
 */

const UploadTracker = (function() {
    'use strict';

    let uploadsRemaining = 0;
    let isInitialized = false;

    // DOM Elements cache
    const elements = {};

    // ════════════════════════════════════════════════════════
    // INITIALIZATION
    // ════════════════════════════════════════════════════════

    function init() {
        if (isInitialized) return;

        // Cache elements
        elements.uploadsLeft = document.getElementById('uploadsLeft');
        elements.bannerUploadsLeft = document.getElementById('bannerUploadsLeft');
        elements.uploadForm = document.getElementById('documentUploadForm');
        elements.submitBtn = document.getElementById('submitBtn');
        elements.noUploadsModal = document.getElementById('noUploadsModal');
        elements.uploadStatusBanner = document.getElementById('uploadStatusBanner');

        // Get initial count
        if (elements.uploadsLeft) {
            uploadsRemaining = parseInt(elements.uploadsLeft.dataset.initial) || 0;
        }

        // Setup form handler
        if (elements.uploadForm) {
            setupFormHandler();
        }

        // Setup file inputs
        setupFileInputs();

        isInitialized = true;
        console.log('UploadTracker initialized. Remaining:', uploadsRemaining);
    }

    // ════════════════════════════════════════════════════════
    // FORM HANDLING
    // ════════════════════════════════════════════════════════

    function setupFormHandler() {
        elements.uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            // Check quota
            if (uploadsRemaining <= 0) {
                showNoUploadsModal();
                return;
            }

            // Submit documents
            const formData = new FormData(this);
            const result = await submitDocuments(formData);

            if (result.success && result.redirect_to) {
                window.location.href = result.redirect_to;
            }
        });
    }

    function setupFileInputs() {
        const cvInput = document.getElementById('cvUpload');
        const jdInput = document.getElementById('jdUpload');
        const cvFileName = document.getElementById('cvFileName');
        const jdFileName = document.getElementById('jdFileName');
        const cvBox = document.getElementById('cvUploadBox');
        const jdBox = document.getElementById('jdUploadBox');

        if (cvInput) {
            cvInput.addEventListener('change', function() {
                if (this.files.length > 0) {
                    cvFileName.textContent = this.files[0].name;
                    cvBox.classList.add('file-selected');
                } else {
                    cvFileName.textContent = 'No file chosen';
                    cvBox.classList.remove('file-selected');
                }
            });
        }

        if (jdInput) {
            jdInput.addEventListener('change', function() {
                if (this.files.length > 0) {
                    jdFileName.textContent = this.files[0].name;
                    jdBox.classList.add('file-selected');
                } else {
                    jdFileName.textContent = 'No file chosen';
                    jdBox.classList.remove('file-selected');
                }
            });
        }

        // Drag and drop
        [cvBox, jdBox].forEach(box => {
            if (!box) return;

            box.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.classList.add('dragover');
            });

            box.addEventListener('dragleave', function() {
                this.classList.remove('dragover');
            });

            box.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('dragover');
                const input = this.closest('.file-upload-container').querySelector('input[type="file"]');
                if (e.dataTransfer.files.length > 0) {
                    input.files = e.dataTransfer.files;
                    input.dispatchEvent(new Event('change'));
                }
            });
        });
    }

    // ════════════════════════════════════════════════════════
    // API CALLS
    // ════════════════════════════════════════════════════════

    async function fetchRemaining() {
        try {
            const response = await fetch('/api/uploads/remaining/', {
                method: 'GET',
                credentials: 'same-origin'
            });
            const data = await response.json();
            if (data.success) {
                uploadsRemaining = data.uploads_remaining;
                updateDisplay();
            }
            return data;
        } catch (error) {
            console.error('Error fetching uploads:', error);
            return null;
        }
    }

    async function submitDocuments(formData) {
        if (uploadsRemaining <= 0) {
            showNoUploadsModal();
            return { success: false, error: 'No uploads remaining' };
        }

        setLoading(true);

        try {
            const csrfToken = getCSRFToken();

            const response = await fetch('/api/documents/submit/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: formData,
                credentials: 'same-origin'
            });

            const data = await response.json();

            setLoading(false);

            if (data.success) {
                uploadsRemaining = data.uploads_remaining;
                updateDisplay();
                animateDecrement();
                showNotification('Documents submitted successfully!', 'success');
                return data;
            } else {
                if (data.redirect_to_bundles) {
                    showNoUploadsModal();
                } else {
                    showNotification(data.error || 'Upload failed', 'error');
                }
                return data;
            }
        } catch (error) {
            setLoading(false);
            console.error('Error submitting:', error);
            showNotification('Network error. Please try again.', 'error');
            return { success: false, error: 'Network error' };
        }
    }

    // ════════════════════════════════════════════════════════
    // UI UPDATES
    // ════════════════════════════════════════════════════════

    function updateDisplay() {
        // Update navbar counter
        if (elements.uploadsLeft) {
            elements.uploadsLeft.textContent = uploadsRemaining;
            elements.uploadsLeft.className = 'uploads-count';

            if (uploadsRemaining <= 0) {
                elements.uploadsLeft.classList.add('count-zero');
                showGetMoreButton();
            } else if (uploadsRemaining === 1) {
                elements.uploadsLeft.classList.add('count-low');
            } else if (uploadsRemaining <= 2) {
                elements.uploadsLeft.classList.add('count-medium');
            } else {
                elements.uploadsLeft.classList.add('count-high');
            }
        }

        // Update banner
        if (elements.bannerUploadsLeft) {
            elements.bannerUploadsLeft.textContent = uploadsRemaining;
        }

        // Update submit button
        if (elements.submitBtn) {
            elements.submitBtn.disabled = uploadsRemaining <= 0;
        }
    }

    function animateDecrement() {
        if (elements.uploadsLeft) {
            elements.uploadsLeft.classList.add('decrement-animation');
            setTimeout(() => {
                elements.uploadsLeft.classList.remove('decrement-animation');
            }, 600);
        }
    }

    function setLoading(isLoading) {
        if (!elements.submitBtn) return;

        const btnText = elements.submitBtn.querySelector('.btn-text');
        const btnLoading = elements.submitBtn.querySelector('.btn-loading');

        if (isLoading) {
            elements.submitBtn.disabled = true;
            if (btnText) btnText.style.display = 'none';
            if (btnLoading) btnLoading.style.display = 'inline-flex';
        } else {
            elements.submitBtn.disabled = uploadsRemaining <= 0;
            if (btnText) btnText.style.display = 'inline-flex';
            if (btnLoading) btnLoading.style.display = 'none';
        }
    }

    function showGetMoreButton() {
        const counter = document.getElementById('uploadsCounter');
        if (!counter || counter.querySelector('.get-more-btn')) return;

        const btn = document.createElement('a');
        btn.href = '/bundles/';
        btn.className = 'btn btn-sm btn-warning ms-2 get-more-btn';
        btn.innerHTML = '<i class="bi bi-plus-circle"></i> Get More';
        counter.appendChild(btn);
    }

    function showNoUploadsModal() {
        if (elements.noUploadsModal) {
            const modal = new bootstrap.Modal(elements.noUploadsModal);
            modal.show();
        } else {
            if (confirm('No uploads remaining. Would you like to purchase more?')) {
                window.location.href = '/bundles/';
            }
        }
    }

    function showNotification(message, type = 'info') {
        const existing = document.querySelector('.upload-notification');
        if (existing) existing.remove();

        const notification = document.createElement('div');
        notification.className = `upload-notification notification-${type}`;

        const icons = { success: 'check-circle', error: 'x-circle', info: 'info-circle' };
        notification.innerHTML = `
            <i class="bi bi-${icons[type]}-fill"></i>
            <span>${message}</span>
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }

    // ════════════════════════════════════════════════════════
    // HELPERS
    // ════════════════════════════════════════════════════════

    function getCSRFToken() {
        const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
        if (cookie) return cookie.split('=')[1];
        const input = document.querySelector('[name=csrfmiddlewaretoken]');
        return input ? input.value : '';
    }

    function canUpload() {
        return uploadsRemaining > 0;
    }

    function getRemaining() {
        return uploadsRemaining;
    }

    // ════════════════════════════════════════════════════════
    // PUBLIC API
    // ════════════════════════════════════════════════════════

    return {
        init,
        submitDocuments,
        canUpload,
        getRemaining,
        refresh: fetchRemaining,
        showNoUploadsModal
    };

})();

// Auto-init on DOM ready
document.addEventListener('DOMContentLoaded', () => UploadTracker.init());

// Global access
window.UploadTracker = UploadTracker;