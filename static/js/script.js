document.addEventListener('DOMContentLoaded', function() {
        // Handle close button clicks using event delegation
        document.getElementById('flash-container').addEventListener('click', function(e) {
            if (e.target.classList.contains('close-flash')) {
                const flashMsg = e.target.closest('.flash-message');
                flashMsg.style.opacity = '0';
                setTimeout(() => flashMsg.remove(), 500);
            }
        });

        // Auto-hide flash messages after 5 seconds
        const flashMessages = document.querySelectorAll('.flash-message');
        flashMessages.forEach(msg => {
            setTimeout(() => {
                msg.style.opacity = '0';
                setTimeout(() => msg.remove(), 500);
            }, 5000);
        });
});

// document.addEventListener('DOMContentLoaded', function() {
//     // Auto-hide flash messages after 5 seconds
//     const flashMessages = document.querySelectorAll('.flash-message');
//
//     flashMessages.forEach(message => {
//         // Add click handler for manual close
//         const closeBtn = message.querySelector('.close-btn');
//         if (closeBtn) {
//             closeBtn.addEventListener('click', () => {
//                 message.style.opacity = '0';
//                 setTimeout(() => message.remove(), 500);
//             });
//         }
//
//         // Auto-hide after 5 seconds
//         setTimeout(() => {
//             message.style.opacity = '0';
//             setTimeout(() => message.remove(), 500);
//         }, 5000);
//     });
//
//
//     // const socket = io();
//     // const bidAmountInput = document.getElementById('bid-amount');
//     // const placeBidButton = document.getElementById('place-bid');
//     // const currentPriceElement = document.getElementById('current-price');
//     // const bidListElement = document.getElementById('bid-list');
//     //
//     // if (placeBidButton) {
//     //     placeBidButton.addEventListener('click', function() {
//     //         const bidAmount = parseFloat(bidAmountInput.value);
//     //         if (isNaN(bidAmount)) {
//     //             alert('Please enter a valid bid amount');
//     //             return;
//     //         }
//     //
//     //         socket.emit('place_bid', {
//     //             auction_id: auctionId,
//     //             bid_amount: bidAmount,
//     //             bidder_id: userId
//     //         });
//     //     });
//     // }
//     //
//     // socket.on('new_bid', function(data) {
//     //     if (data.auction_id === auctionId) {
//     //         const bidItem = document.createElement('li');
//     //         bidItem.textContent = `$${data.bid_amount} by ${data.bidder_id} at ${new Date(data.timestamp).toLocaleString()}`;
//     //         bidListElement.prepend(bidItem);
//     //     }
//     // });
//     //
//     // socket.on('update_price', function(data) {
//     //     if (data.auction_id === auctionId) {
//     //         currentPriceElement.textContent = data.current_price;
//     //         bidAmountInput.min = data.current_price;
//     //     }
//     // });
//     //
//     // socket.on('bid_error', function(data) {
//     //     alert(data.message);
//     // });
//     //
//     // // Form validation
//     // const forms = document.querySelectorAll('.needs-validation');
//     // Array.from(forms).forEach(form => {
//     //     form.addEventListener('submit', function(event) {
//     //         if (!form.checkValidity()) {
//     //             event.preventDefault();
//     //             event.stopPropagation();
//     //         }
//     //         form.classList.add('was-validated');
//     //     }, false);
//     // });
//     //
//     // // Date validation - ensure end time is in future
//     // const endTimeInput = document.getElementById('end_time');
//     // endTimeInput.min = new Date().toISOString().slice(0, 16);
//     //
//     // // Image preview functionality
//     // const imageInput = document.getElementById('images');
//     // const previewContainer = document.querySelector('.image-preview-container');
//     //
//     // imageInput.addEventListener('change', function() {
//     //     previewContainer.innerHTML = '';
//     //     const files = this.files;
//     //
//     //     if (files.length > 5) {
//     //         alert('Maximum 5 images allowed. Only the first 5 will be uploaded.');
//     //         imageInput.value = '';
//     //         return;
//     //     }
//     //
//     //     for (let i = 0; i < Math.min(files.length, 5); i++) {
//     //         const file = files[i];
//     //         if (!file.type.match('image.*')) continue;
//     //
//     //         const reader = new FileReader();
//     //         reader.onload = function(e) {
//     //             const preview = document.createElement('div');
//     //             preview.className = 'image-preview';
//     //             preview.innerHTML = `
//     //                 <img src="${e.target.result}" class="img-thumbnail" style="height: 100px; width: auto;">
//     //                 <div class="position-absolute top-0 end-0 bg-danger text-white rounded-circle p-1"
//     //                      style="cursor: pointer; font-size: 0.8rem;"
//     //                      onclick="this.parentNode.remove(); updateFileInput()">×</div>
//     //             `;
//     //             preview.style.position = 'relative';
//     //             previewContainer.appendChild(preview);
//     //         };
//     //         reader.readAsDataURL(file);
//     //     }
//     // });
//     //
//     // // Update file input when preview images are removed
//     // window.updateFileInput = function() {
//     //     const dataTransfer = new DataTransfer();
//     //     const previews = document.querySelectorAll('.image-preview img');
//     //
//     //     Array.from(imageInput.files).forEach(file => {
//     //         let fileUsed = false;
//     //         previews.forEach(preview => {
//     //             if (preview.src.includes(file.name)) {
//     //                 fileUsed = true;
//     //             }
//     //         });
//     //         if (fileUsed) dataTransfer.items.add(file);
//     //     });
//     //
//     //     imageInput.files = dataTransfer.files;
//     // };
//
// });