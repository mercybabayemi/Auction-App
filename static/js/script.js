document.addEventListener('DOMContentLoaded', function() {
      // The socket is already initialized in base.html
    console.log("Socket status:", socket.connected);

    // ========== Flash Message Handling ==========
    const flashMessages = document.querySelectorAll('.flash-message');
    const flashContainer = document.getElementById('flash-container');

    // Auto-hide after 5 seconds
    if (flashMessages.length > 0) {
        flashMessages.forEach(msg => {
            setTimeout(() => {
                msg.style.transition = 'opacity 0.5s ease';
                msg.style.opacity = '0';
                setTimeout(() => msg.remove(), 500);
            }, 5000);
        });
    }

    // Close button click handler
    if (flashContainer) {
        flashContainer.addEventListener('click', function(e) {
            if (e.target.classList.contains('close-flash')) {
                const flashMsg = e.target.closest('.flash-message');
                if (flashMsg) {
                    flashMsg.style.transition = 'opacity 0.5s ease';
                    flashMsg.style.opacity = '0';
                    setTimeout(() => flashMsg.remove(), 500);
                }
            }
        });
    }

    //Delete Profile Modal
    const deleteProfileBtn = document.getElementById('deleteProfileBtn');
    const modal = document.getElementById('deleteModal');
    const closeBtn = document.querySelector('.close');
    const cancelBtn = document.querySelector('.btn-cancel');

    // Only add event listeners if elements exist
    if (deleteProfileBtn && modal) {
        deleteProfileBtn.addEventListener('click', () => {
            modal.style.display = 'block';
        });
    }

    if (closeBtn && modal) {
        closeBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }

    if (cancelBtn && modal) {
        cancelBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }

    if (modal) {
        window.addEventListener('click', (event) => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    }

    // Get elements from the DOM
    const bidForm = document.getElementById('bid-form');
    const bidAmountInput = document.getElementById('bid-amount');
    const currentPriceElement = document.getElementById('current-price');
    const bidHistoryList = document.getElementById('bid-history-list');
    const countdownElement = document.getElementById('countdown-timer');

    // Only run bidding logic if on auction detail page
    if (bidForm) {
        // Handle bid form submission
        bidForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const bidAmount = parseFloat(bidAmountInput.value);
            if (isNaN(bidAmount)) {
                alert('Please enter a valid bid amount');
                return;
            }

            // Emit the bid to the server
            socket.emit('place_bid', {
                auction_id: auctionId,
                bid_amount: bidAmount
            });
        });

        // Handle new bid event from server
        socket.on('new_bid', function(data) {
            if (data.auction_id === auctionId) {
                // Update current price display
                currentPriceElement.textContent = data.bid_amount.toFixed(2);

                // Add bid to history
                const bidItem = document.createElement('div');
                bidItem.className = 'bid-item';
                bidItem.innerHTML = `
                    <span class="bidder">${data.bidder_name}</span>
                    <span class="amount">$${data.bid_amount.toFixed(2)}</span>
                    <span class="time">${new Date(data.timestamp).toLocaleTimeString()}</span>
                `;

                // Highlight if it's the current user's bid
                if (data.bidder_id === currentUserId) {
                    bidItem.classList.add('highest-bid');
                }

                bidHistoryList.prepend(bidItem);

                // Update minimum bid amount
                bidAmountInput.min = (data.bid_amount + 0.01).toFixed(2);
            }
        });

        // Handle price updates
        socket.on('update_price', function(data) {
            if (data.auction_id === auctionId) {
                currentPriceElement.textContent = data.current_price.toFixed(2);
                bidAmountInput.min = (data.current_price + 0.01).toFixed(2);
            }
        });

        // Handle bid errors
        socket.on('bid_error', function(data) {
            alert(data.message);
        });
    }

    // Countdown timer for auction end
    if (countdownElement) {
        const endTime = new Date(countdownElement.dataset.endtime).getTime();

        function updateCountdown() {
            const now = new Date().getTime();
            const distance = endTime - now;

            if (distance < 0) {
                countdownElement.textContent = "Auction ended";
                if (bidForm) bidForm.style.display = 'none';
                return;
            }

            // Calculate days, hours, minutes, seconds
            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            // Display the result
            let countdownText = '';
            if (days > 0) countdownText += `${days}d `;
            if (hours > 0 || days > 0) countdownText += `${hours}h `;
            countdownText += `${minutes}m ${seconds}s`;

            countdownElement.textContent = countdownText;
        }

        // Update every second
        updateCountdown();
        setInterval(updateCountdown, 1000);
    }


    //Handling preview image section
    const imageInput = document.getElementById('images');
    const previewContainer = document.querySelector('.image-preview-container');
    const maxFiles = 5;

    // If cloudinary.js is loaded and configured for unsigned uploads, let it handle preview/upload.
    // We check window.CLOUDINARY_UNSIGNED_PRESET which you set in base.html.
    if (window && window.CLOUDINARY_UNSIGNED_PRESET) {
        console.log('cloudinary.js present - skipping preview logic in script.js');
    } else {
        // Fallback preview logic (only used when cloudinary.js is not present).
        if (imageInput) {
            // Keep a local array of files to allow cumulative previews
            let selectedFilesLocal = [];

            imageInput.addEventListener('change', function(event) {
                const newFiles = Array.from(event.target.files);

                // Check total count
                if (selectedFilesLocal.length + newFiles.length > maxFiles) {
                    alert(`You can upload a maximum of ${maxFiles} images`);
                    return;
                }

                // Append new files and show previews for each
                newFiles.forEach((file) => {
                    // Validate
                    if (!file.type.match('image.*')) {
                        alert('Only image files are allowed');
                        return;
                    }
                    if (file.size > 5 * 1024 * 1024) {
                        alert('Each file must be under 5 MB.');
                        return;
                    }

                    // prevent duplicate (same name + size)
                    const isDuplicate = selectedFilesLocal.some(f => f.name === file.name && f.size === file.size);
                    if (isDuplicate) {
                        console.log('Skipping duplicate file:', file.name);
                        return;
                    }

                    selectedFilesLocal.push(file);

                    // create preview element
                    const previewElement = document.createElement('div');
                    previewElement.className = 'image-preview-item position-relative';
                    previewElement.style.width = '150px';
                    previewElement.style.height = '150px';
                    previewElement.style.border = '1px solid #ddd';
                    previewElement.style.borderRadius = '4px';
                    previewElement.style.overflow = 'hidden';
                    previewElement.style.display = 'inline-block';
                    previewElement.style.marginRight = '10px';

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
                        const idx = selectedFilesLocal.indexOf(file);
                        if (idx > -1) selectedFilesLocal.splice(idx, 1);
                        previewElement.remove();
                        if (selectedFilesLocal.length === 0) {
                            imageInput.value = '';
                        }
                    });

                    const reader = new FileReader();
                    reader.onload = function (e) {
                        img.src = e.target.result;
                        previewElement.appendChild(img);
                        previewElement.appendChild(removeBtn);
                        previewContainer.appendChild(previewElement);
                    };
                    reader.readAsDataURL(file);
                });
            });
        }
    }

    function updateFileInput(allFiles, fileToRemove) {
        // Create new DataTransfer object
        const dataTransfer = new DataTransfer();

        // Add all files except the removed one
        for (let i = 0; i < allFiles.length; i++) {
            if (allFiles[i] !== fileToRemove) {
                dataTransfer.items.add(allFiles[i]);
            }
        }

        // Update the file input
        imageInput.files = dataTransfer.files;
    }


                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          // Thumbnail click handler
    document.querySelectorAll('.thumbnail').forEach(thumb => {
        thumb.addEventListener('click', function() {
            const mainImage = document.getElementById('main-auction-image');
            if (mainImage) {
                mainImage.src = this.dataset.imageSrc;
            }
            document.querySelectorAll('.thumbnail').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });
});