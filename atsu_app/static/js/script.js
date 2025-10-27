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
    const signInBtn = document.getElementById('signInBtn');
    const signUpBtn = document.getElementById('signUpBtn');

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

    // Sign In/Sign Up button handlers
    signInBtn.addEventListener('click', function(e) {
        e.preventDefault();
        alert('Sign In functionality coming soon!');
    });

    signUpBtn.addEventListener('click', function(e) {
        e.preventDefault();
        alert('Sign Up functionality coming soon!');
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

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});