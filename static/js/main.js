/* ===================================
   DCDS Project - Main JavaScript
   Air Quality Monitoring System
   =================================== */

// Document Ready
$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow', function() {
            $(this).remove();
        });
    }, 5000);
    
    // Add fade-in animation to cards
    $('.card').addClass('fade-in');
    
    // Confirm delete actions
    $('.btn-danger').on('click', function(e) {
        if ($(this).attr('onclick')) {
            return; // Skip if onclick handler exists
        }
        if (!confirm('Are you sure you want to delete this item?')) {
            e.preventDefault();
        }
    });
    
    // Form validation feedback
    $('form').on('submit', function(e) {
        var form = $(this)[0];
        if (!form.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
        }
        $(form).addClass('was-validated');
    });
    
    // Search/filter functionality for tables (if not using DataTables)
    $('#searchInput').on('keyup', function() {
        var value = $(this).val().toLowerCase();
        $('table tbody tr').filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
        });
    });
    
    // Smooth scroll to top
    $('#scrollToTop').on('click', function(e) {
        e.preventDefault();
        $('html, body').animate({scrollTop: 0}, 'slow');
    });
    
    // Show loading spinner on form submit
    $('form').on('submit', function() {
        $(this).find('button[type="submit"]').html(
            '<span class="spinner-border spinner-border-sm me-2"></span>Loading...'
        ).prop('disabled', true);
    });
});

// ========== Utility Functions ==========

// Format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Get AQI category based on value
function getAQICategory(value) {
    if (value <= 50) return { category: 'Good', color: 'success' };
    if (value <= 100) return { category: 'Moderate', color: 'info' };
    if (value <= 150) return { category: 'Unhealthy for Sensitive', color: 'warning' };
    if (value <= 200) return { category: 'Unhealthy', color: 'orange' };
    if (value <= 300) return { category: 'Very Unhealthy', color: 'danger' };
    return { category: 'Hazardous', color: 'dark' };
}

// Convert date to readable format
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Show toast notification
function showToast(message, type = 'info') {
    const bgColor = type === 'success' ? 'bg-success' : 
                    type === 'error' ? 'bg-danger' : 
                    type === 'warning' ? 'bg-warning' : 'bg-info';
    
    const toastHTML = `
        <div class="toast align-items-center text-white ${bgColor} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    const toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
    toastContainer.innerHTML = toastHTML;
    document.body.appendChild(toastContainer);
    
    const toastElement = toastContainer.querySelector('.toast');
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    toastElement.addEventListener('hidden.bs.toast', function () {
        toastContainer.remove();
    });
}

// ========== Chart Helper Functions ==========

// Create gradient for charts
function createGradient(ctx, color1, color2) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, color1);
    gradient.addColorStop(1, color2);
    return gradient;
}

// Chart.js default configuration
Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = '#2c3e50';

// ========== Data Export Functions ==========

// Export table to CSV
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    let csv = [];
    
    // Get headers
    const headers = [];
    table.querySelectorAll('thead th').forEach(th => {
        headers.push(th.textContent.trim());
    });
    csv.push(headers.join(','));
    
    // Get rows
    table.querySelectorAll('tbody tr').forEach(tr => {
        const row = [];
        tr.querySelectorAll('td').forEach(td => {
            row.push('"' + td.textContent.trim().replace(/"/g, '""') + '"');
        });
        csv.push(row.join(','));
    });
    
    // Download
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename + '.csv';
    link.click();
}

// Print table
function printTable(elementId) {
    const printContents = document.getElementById(elementId).innerHTML;
    const originalContents = document.body.innerHTML;
    document.body.innerHTML = printContents;
    window.print();
    document.body.innerHTML = originalContents;
    location.reload();
}

// ========== AJAX Helper Functions ==========

// Fetch data with loading indicator
async function fetchData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
        showToast('Error loading data', 'error');
        return null;
    }
}

// Post data with AJAX
async function postData(url, data) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        return await response.json();
    } catch (error) {
        console.error('Error posting data:', error);
        showToast('Error submitting data', 'error');
        return null;
    }
}

// ========== Form Utilities ==========

// Reset form
function resetForm(formId) {
    document.getElementById(formId).reset();
}

// Validate email
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Validate phone
function validatePhone(phone) {
    const re = /^[\d\s\-\+\(\)]+$/;
    return re.test(phone);
}

// ========== Local Storage Utilities ==========

// Save to localStorage
function saveToLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
        console.error('Error saving to localStorage:', e);
    }
}

// Get from localStorage
function getFromLocalStorage(key) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    } catch (e) {
        console.error('Error getting from localStorage:', e);
        return null;
    }
}

// Remove from localStorage
function removeFromLocalStorage(key) {
    try {
        localStorage.removeItem(key);
    } catch (e) {
        console.error('Error removing from localStorage:', e);
    }
}

// ========== Dark Mode Toggle (Optional Feature) ==========

// Check for saved dark mode preference
if (getFromLocalStorage('darkMode') === true) {
    document.body.classList.add('dark-mode');
}

// Toggle dark mode
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDarkMode = document.body.classList.contains('dark-mode');
    saveToLocalStorage('darkMode', isDarkMode);
}

// ========== Refresh Data ==========

// Auto-refresh dashboard data every 5 minutes
function autoRefreshDashboard() {
    setInterval(function() {
        location.reload();
    }, 300000); // 5 minutes
}

// ========== Search and Filter ==========

// Real-time search
function liveSearch(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    const rows = table.getElementsByTagName('tr');
    
    input.addEventListener('keyup', function() {
        const filter = input.value.toLowerCase();
        
        for (let i = 1; i < rows.length; i++) {
            const row = rows[i];
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(filter) ? '' : 'none';
        }
    });
}

// ========== Initialization ==========

// Initialize all interactive elements
function initializeApp() {
    console.log('DCDS Project initialized successfully');
    
    // Initialize tooltips and popovers
    $('[data-bs-toggle="tooltip"]').tooltip();
    $('[data-bs-toggle="popover"]').popover();
    
    // Add smooth scrolling
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        const target = $(this.hash);
        if (target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top - 70
            }, 800);
        }
    });
}

// Call initialization
$(document).ready(function() {
    initializeApp();
});

// ========== Console Banner ==========
console.log('%c DCDS Project ', 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-size: 20px; padding: 10px;');
console.log('%c Air Quality and Environmental Data Collection System ', 'color: #667eea; font-size: 14px;');
console.log('%c Developed for Academic Mini-Project | 2025 ', 'color: #999; font-size: 12px;');
