// Toggle between login and registration forms - MUST be global for onclick
function toggleForms(event) {
    event.preventDefault();

    const registerForm = document.getElementById('register-form');
    const loginForm = document.getElementById('login-form');

    registerForm.classList.toggle('hidden');
    loginForm.classList.toggle('hidden');

    // Clear any error messages when switching
    const messages = document.querySelector('.auth-messages');
    if (messages) {
        messages.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const form = document.getElementById('documentUploadForm');
    const cvUpload = document.getElementById('cvUpload');
    const jdUpload = document.getElementById('jdUpload');
    const cvFileName = document.getElementById('cvFileName');
    const jdFileName = document.getElementById('jdFileName');
    const cvUploadBox = document.getElementById('cvUploadBox');
    const jdUploadBox = document.getElementById('jdUploadBox');
    const uploadStatus = document.getElementById('uploadStatus');
    const uploadsLeft = document.getElementById('uploadsLeft');
    const moreBtn = document.getElementById('moreBtn');

    // Initialize uploads left from localStorage or default to 3
    let remainingUploads = localStorage.getItem('remainingUploads') || 3;
    updateUploadsCounter();

    // File upload handling
    function handleFileSelect(fileInput, fileNameElement, uploadBox) {
        if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            fileNameElement.textContent = file.name;
            uploadBox.classList.add('file-selected');
        } else {
            fileNameElement.textContent = 'No file chosen';
            uploadBox.classList.remove('file-selected');
        }
    }

    // Drag and drop functionality
    function setupDragAndDrop(dropZone, fileInput) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        function highlight() {
            dropZone.classList.add('dragover');
        }

        function unhighlight() {
            dropZone.classList.remove('dragover');
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });

        dropZone.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length) {
                fileInput.files = files;
                const event = new Event('change');
                fileInput.dispatchEvent(event);
            }
        }
    }

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Update uploads counter
    function updateUploadsCounter() {
        uploadsLeft.textContent = remainingUploads;
        localStorage.setItem('remainingUploads', remainingUploads);
    }

    // Event Listeners
    cvUpload.addEventListener('change', () => handleFileSelect(cvUpload, cvFileName, cvUploadBox));
    jdUpload.addEventListener('change', () => handleFileSelect(jdUpload, jdFileName, jdUploadBox));

    // Setup drag and drop
    setupDragAndDrop(cvUploadBox, cvUpload);
    setupDragAndDrop(jdUploadBox, jdUpload);

    // More button click handler
    moreBtn.addEventListener('click', function() {
        alert('Premium features coming soon!');
    });

    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        if (remainingUploads <= 0) {
            showStatus('You have no uploads left. Please upgrade your plan.', 'error');
            return;
        }

        const formData = new FormData(form);

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Uploading...';

        // Simulate API call (replace with actual API call)
        setTimeout(() => {
            // Decrement remaining uploads
            remainingUploads--;
            updateUploadsCounter();

            // Reset form and show success message
            form.reset();
            cvFileName.textContent = 'No file chosen';
            jdFileName.textContent = 'No file chosen';
            cvUploadBox.classList.remove('file-selected');
            jdUploadBox.classList.remove('file-selected');
            showStatus('Documents uploaded successfully!', 'success');

            // Reset button state
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;

            // Log to console (for demo)
            console.log('Form submitted with:', {
                cv: cvUpload.files[0]?.name,
                jobDescription: jdUpload.files[0]?.name
            });
        }, 1500);
    });

    // Show status message
    function showStatus(message, type) {
        uploadStatus.textContent = message;
        uploadStatus.className = 'status-message';
        uploadStatus.classList.add(type);

        // Hide message after 5 seconds
        setTimeout(() => {
            uploadStatus.classList.remove(type);
            uploadStatus.textContent = '';
        }, 5000);
    }

    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Auto-hide success messages after 5 seconds
    const successMessages = document.querySelectorAll('.auth-message.success');
    successMessages.forEach(message => {
        setTimeout(() => {
            message.style.animation = 'slideDown 0.3s ease reverse';
            setTimeout(() => {
                message.style.display = 'none';
            }, 300);
        }, 5000);
    });

    // If there are messages (errors or success), show the modal
    const authMessages = document.querySelector('.auth-messages');
    if (authMessages && authMessages.children.length > 0) {
        const authModal = new bootstrap.Modal(document.getElementById('authModal'));
        authModal.show();
    }

    // Password strength indicator
    const passwordInput = document.getElementById('reg-password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;

            // Example: minimum length check
            if (password.length === 0) {
                this.style.borderColor = '#ddd';
            } else if (password.length < 8) {
                this.style.borderColor = '#ffc107';
            } else {
                this.style.borderColor = '#28a745';
            }
        });
    }
});