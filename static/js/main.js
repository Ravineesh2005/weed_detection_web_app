document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const previewSection = document.getElementById('preview-section');
    const imagePreview = document.getElementById('image-preview');
    const scanBtn = document.getElementById('scan-btn');
    
    const resultsCard = document.getElementById('results-card');
    const resultImage = document.getElementById('result-image');
    const weedCount = document.getElementById('weed-count');
    const resetBtn = document.getElementById('reset-btn');
    const uploadCard = document.querySelector('.upload-card');

    let currentFile = null;

    // Drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', handleFileSelect, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFileSelect(e) {
        const files = e.target.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                currentFile = file;
                showPreview(file);
            } else {
                alert('Please upload a valid image file (JPEG/PNG).');
            }
        }
    }

    function showPreview(file) {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = () => {
            imagePreview.src = reader.result;
            dropZone.style.display = 'none';
            previewSection.style.display = 'block';
        }
    }

    scanBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        // UI Loading state
        scanBtn.disabled = true;
        scanBtn.innerHTML = 'Analyzing Environment... <span class="loader"></span>';
        
        const formData = new FormData();
        formData.append('image', currentFile);

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const text = await response.text();
                throw new Error(text || 'Network response was not ok');
            }

            const data = await response.json();

            if (data.success) {
                // Hide upload, show results with a slight delay for smooth transition
                uploadCard.style.display = 'none';
                
                weedCount.textContent = data.count;
                
                // Add bounding boxes rendered image from backend
                if(data.image_base64) {
                    resultImage.src = `data:image/jpeg;base64,${data.image_base64}`;
                } else {
                    // Fall back to original image if no annotated base64 returned
                    resultImage.src = imagePreview.src;
                }
                
                resultsCard.style.display = 'block';
                
                // Smooth scroll to results
                resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
                alert(data.error || 'An error occurred during prediction.');
            }
        } catch (error) {
            console.error('API Error:', error);
            alert('Failed to analyze the image. Please try again or check server logs. ' + error.message);
        } finally {
            // Reset button state
            scanBtn.disabled = false;
            scanBtn.innerHTML = 'Scan for Weeds';
        }
    });

    resetBtn.addEventListener('click', () => {
        currentFile = null;
        fileInput.value = '';
        resultsCard.style.display = 'none';
        previewSection.style.display = 'none';
        dropZone.style.display = 'block';
        uploadCard.style.display = 'block';
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});
