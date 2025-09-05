// static/js/cloudinary.js
(function () {
  const MAX_FILES = 5;
  const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
  const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];

  function makeUid() {
    return `${Date.now()}-${Math.floor(Math.random() * 1e6)}`;
  }

  async function uploadSingleFileToCloudinary(file) {
    const url = `https://api.cloudinary.com/v1_1/${window.CLOUDINARY_CLOUD_NAME}/image/upload`;
    const fd = new FormData();
    fd.append('file', file);
    fd.append('upload_preset', window.CLOUDINARY_UNSIGNED_PRESET);
    fd.append('folder', 'auction_app/images'); // ensures images stored in this folder
    const res = await fetch(url, { method: 'POST', body: fd });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Cloudinary upload failed: ${res.status} ${text}`);
    }
    return res.json();
  }

  document.addEventListener('DOMContentLoaded', () => {
    const createForm = document.querySelector('form[action$="/create"]');
    const fileInput = document.getElementById('images');
    const previewContainer = document.querySelector('.image-preview-container');

    if (!createForm || !fileInput || !previewContainer) return;

    // Selected files list holds objects: { id, file, previewElement }
    const selectedFiles = [];

    // Spinner feedback
    const spinner = document.createElement('div');
    spinner.innerText = "Uploading images...";
    spinner.style.display = "none";
    spinner.style.color = "blue";
    spinner.style.fontWeight = "bold";
    createForm.appendChild(spinner);

    function addPreviewForFile(fileObj) {
      const { id, file } = fileObj;

      const previewElement = document.createElement('div');
      previewElement.className = 'image-preview-item position-relative';
      previewElement.style.width = '150px';
      previewElement.style.height = '150px';
      previewElement.style.border = '1px solid #ddd';
      previewElement.style.borderRadius = '4px';
      previewElement.style.overflow = 'hidden';
      previewElement.style.marginRight = '10px';
      previewElement.style.display = 'inline-block';
      previewElement.dataset.uid = id;

      const img = document.createElement('img');
      img.style.width = '100%';
      img.style.height = '100%';
      img.style.objectFit = 'cover';

      const removeBtn = document.createElement('button');
      removeBtn.innerHTML = '&times;';
      removeBtn.className = 'btn btn-danger btn-sm position-absolute top-0 end-0';
      removeBtn.style.padding = '0.1rem 0.3rem';
      removeBtn.style.borderRadius = '50%';
      removeBtn.style.cursor = 'pointer';

      removeBtn.addEventListener('click', function (e) {
        e.preventDefault();
        // find index by uid and remove
        const idx = selectedFiles.findIndex(obj => obj.id === id);
        if (idx > -1) {
          // remove from array
          selectedFiles.splice(idx, 1);
        }
        // remove preview DOM
        previewElement.remove();

        // Remove any hidden inputs that might exist (e.g. stale from previous upload attempt)
        const hiddenInputs = createForm.querySelectorAll('input[name="image_urls"]');
        // It's safer to remove all hidden inputs and recreate them on submit rather than manipulating by idx.
        if (hiddenInputs.length > 0) {
          hiddenInputs.forEach(inp => inp.remove());
        }

        // reset native input if no files remain
        if (selectedFiles.length === 0) {
          fileInput.value = '';
        }
      });

      const reader = new FileReader();
      reader.onload = function (e) {
        img.src = e.target.result;
        previewElement.appendChild(img);
        previewElement.appendChild(removeBtn);
        previewContainer.appendChild(previewElement);
        // keep a ref to preview in the fileObj
        fileObj.previewElement = previewElement;
      };
      reader.readAsDataURL(file);
    }

    fileInput.addEventListener('change', (event) => {
      const newFiles = Array.from(event.target.files);

      // Prevent exceeding max files
      if (selectedFiles.length + newFiles.length > MAX_FILES) {
        alert(`You can upload a maximum of ${MAX_FILES} images`);
        return;
      }

      newFiles.forEach((file) => {
        // Validate
        if (!ALLOWED_TYPES.includes(file.type)) {
          alert('Only JPG/PNG/WebP/GIF formats are allowed.');
          return;
        }
        if (file.size > MAX_FILE_SIZE) {
          alert('Each file must be under 5 MB.');
          return;
        }

        // Skip duplicates by name+size
        const duplicate = selectedFiles.some(obj => obj.file.name === file.name && obj.file.size === file.size);
        if (duplicate) {
          console.log('Skipping duplicate:', file.name);
          return;
        }

        // create fileObj and append
        const fileObj = {
          id: makeUid(),
          file: file,
          previewElement: null
        };
        selectedFiles.push(fileObj);
        addPreviewForFile(fileObj);
      });

      // Clear the native input to allow reselection (we manage the files via selectedFiles)
      fileInput.value = '';
    });

    // Form submit interception
    createForm.addEventListener('submit', async (e) => {
      // If hidden inputs already exist (e.g., form was re-submitted), allow submission
      if (createForm.querySelectorAll('input[name="image_urls"]').length > 0) {
        return;
      }

      if (!selectedFiles || selectedFiles.length === 0) {
        e.preventDefault();
        alert('Please upload at least one image.');
        return;
      }

      e.preventDefault();
      try {
        const submitBtn = createForm.querySelector('button[type="submit"], input[type="submit"]');
        if (submitBtn) submitBtn.disabled = true;
        spinner.style.display = "block";

        // Upload files in current order of selectedFiles
        const uploadPromises = selectedFiles.map(obj => uploadSingleFileToCloudinary(obj.file));
        const results = await Promise.all(uploadPromises);

        // Debug logging: show entire responses in browser console
        results.forEach((res, idx) => {
          console.log(`File #${idx} Cloudinary full response:`, res);
        });

        // Remove any pre-existing hidden inputs (just to be safe)
        const priorHidden = createForm.querySelectorAll('input[name="image_urls"]');
        if (priorHidden.length > 0) priorHidden.forEach(i => i.remove());

        // Create hidden inputs in the same order as uploaded results
        results.forEach((res, idx) => {
          const imageUrl = res.secure_url || res.url;
          if (!imageUrl) {
            console.error(`No URL returned for file ${idx}:`, res);
            throw new Error('No URL returned from Cloudinary for file #' + idx);
          }
          console.log(`File #${idx} upload URL to be sent to backend:`, imageUrl);

          const inp = document.createElement('input');
          inp.type = 'hidden';
          inp.name = 'image_urls';
          inp.value = imageUrl;
          createForm.appendChild(inp);
        });

        // Finally remove input element (so server doesn't parse file binaries) and submit
        if (fileInput.parentNode) {
          fileInput.parentNode.removeChild(fileInput);
        }

        createForm.submit();
      } catch (err) {
        console.error('Upload error:', err);
        alert('Image upload failed. Check console for details.');
      } finally {
        spinner.style.display = "none";
        const submitBtn = createForm.querySelector('button[type="submit"], input[type="submit"]');
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  });
})();
