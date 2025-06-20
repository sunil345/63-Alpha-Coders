// Global variables
let categoryChart, priorityChart;
let currentData = {};

// API base URL
const API_BASE = '/api/v1';

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    loadDashboardData();
    setupEventListeners();
    
    // Auto-refresh every 5 minutes
    setInterval(loadDashboardData, 300000);
});

// Setup event listeners
function setupEventListeners() {
    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', loadDashboardData);
    
    // Settings button
    document.getElementById('settingsBtn').addEventListener('click', openSettings);
    document.getElementById('closeSettings').addEventListener('click', closeSettings);
    document.getElementById('saveSettings').addEventListener('click', saveSettings);
    
    // Action buttons
    document.getElementById('analyzeBtn').addEventListener('click', analyzeEmails);
    document.getElementById('summaryBtn').addEventListener('click', generateSummary);
    document.getElementById('voiceBtn').addEventListener('click', generateVoiceSummary);
    document.getElementById('notifyBtn').addEventListener('click', sendNotifications);
    
    // Close modal when clicking outside
    document.getElementById('settingsModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeSettings();
        }
    });
}

// Initialize charts
function initializeCharts() {
    // Category chart
    const categoryCtx = document.getElementById('categoryChart').getContext('2d');
    categoryChart = new Chart(categoryCtx, {
        type: 'doughnut',
        data: {
            labels: ['Work', 'Personal', 'Promotions', 'Social', 'Other'],
            datasets: [{
                data: [0, 0, 0, 0, 0],
                backgroundColor: [
                    '#3B82F6',
                    '#10B981',
                    '#F59E0B',
                    '#8B5CF6',
                    '#6B7280'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });

    // Priority chart
    const priorityCtx = document.getElementById('priorityChart').getContext('2d');
    priorityChart = new Chart(priorityCtx, {
        type: 'bar',
        data: {
            labels: ['Low', 'Medium', 'High', 'Urgent'],
            datasets: [{
                label: 'Emails',
                data: [0, 0, 0, 0],
                backgroundColor: [
                    '#6B7280',
                    '#3B82F6',
                    '#F59E0B',
                    '#EF4444'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Load dashboard data
async function loadDashboardData() {
    showLoading(true);
    
    try {
        const today = new Date().toISOString().split('T')[0];
        
        // Get today's summary
        const summaryResponse = await fetch(`${API_BASE}/emails/summary/${today}`);
        if (summaryResponse.ok) {
            const summary = await summaryResponse.json();
            updateDashboard(summary);
        } else {
            // If no summary exists, get emails and create one
            await analyzeEmails();
        }
        
        // Load urgent emails
        await loadUrgentEmails();
        
        // Load unread emails
        await loadUnreadEmails();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showNotification('Error loading data', 'error');
    } finally {
        showLoading(false);
    }
}

// Update dashboard with data
function updateDashboard(data) {
    currentData = data;
    
    // Update status cards
    document.getElementById('totalEmails').textContent = data.total_emails || 0;
    document.getElementById('urgentEmails').textContent = data.urgent_emails?.length || 0;
    document.getElementById('unreadEmails').textContent = data.unread_emails?.length || 0;
    document.getElementById('needReply').textContent = data.response_reminders?.length || 0;
    
    // Update charts
    updateCategoryChart(data.categories || {});
    updatePriorityChart(data.priority_breakdown || {});
}

// Update category chart
function updateCategoryChart(categories) {
    const labels = Object.keys(categories);
    const data = Object.values(categories);
    
    categoryChart.data.labels = labels;
    categoryChart.data.datasets[0].data = data;
    categoryChart.update();
}

// Update priority chart
function updatePriorityChart(priorities) {
    const labels = Object.keys(priorities);
    const data = Object.values(priorities);
    
    priorityChart.data.labels = labels;
    priorityChart.data.datasets[0].data = data;
    priorityChart.update();
}

// Load urgent emails
async function loadUrgentEmails() {
    try {
        const response = await fetch(`${API_BASE}/emails/urgent?limit=10`);
        if (response.ok) {
            const emails = await response.json();
            displayEmails('urgentEmailsList', emails, 'urgent');
        }
    } catch (error) {
        console.error('Error loading urgent emails:', error);
    }
}

// Load unread emails
async function loadUnreadEmails() {
    try {
        const response = await fetch(`${API_BASE}/emails/unread?limit=10`);
        if (response.ok) {
            const emails = await response.json();
            displayEmails('unreadEmailsList', emails, 'unread');
        }
    } catch (error) {
        console.error('Error loading unread emails:', error);
    }
}

// Display emails in a list
function displayEmails(containerId, emails, type) {
    const container = document.getElementById(containerId);
    
    if (!emails || emails.length === 0) {
        container.innerHTML = `
            <div class="p-4 text-center text-gray-500">
                <i class="fas fa-inbox text-2xl mb-2"></i>
                <p>No ${type} emails</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = emails.map(email => `
        <div class="p-4 priority-${email.priority}">
            <div class="flex justify-between items-start">
                <div class="flex-1">
                    <h4 class="font-medium text-gray-900 truncate">${email.subject}</h4>
                    <p class="text-sm text-gray-600">From: ${email.sender}</p>
                    <p class="text-xs text-gray-500">${new Date(email.received_at).toLocaleString()}</p>
                    <p class="text-sm text-gray-700 mt-2">${email.summary}</p>
                </div>
                <div class="ml-4 flex space-x-2">
                    <button onclick="markAsRead('${email.id}')" class="text-blue-600 hover:text-blue-800">
                        <i class="fas fa-check"></i>
                    </button>
                    <button onclick="markAsReplied('${email.id}')" class="text-green-600 hover:text-green-800">
                        <i class="fas fa-reply"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Analyze emails
async function analyzeEmails() {
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/emails/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                date_range: 'today',
                include_archived: false
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            updateDashboard(result);
            showNotification('Emails analyzed successfully', 'success');
        } else {
            throw new Error('Failed to analyze emails');
        }
    } catch (error) {
        console.error('Error analyzing emails:', error);
        showNotification('Error analyzing emails', 'error');
    } finally {
        showLoading(false);
    }
}

// Generate summary
async function generateSummary() {
    showLoading(true);
    
    try {
        const today = new Date().toISOString().split('T')[0];
        const response = await fetch(`${API_BASE}/emails/natural-summary/${today}`);
        
        if (response.ok) {
            const result = await response.json();
            showNotification(result.summary, 'info');
        } else {
            throw new Error('Failed to generate summary');
        }
    } catch (error) {
        console.error('Error generating summary:', error);
        showNotification('Error generating summary', 'error');
    } finally {
        showLoading(false);
    }
}

// Generate voice summary
async function generateVoiceSummary() {
    showLoading(true);
    
    try {
        const today = new Date().toISOString().split('T')[0];
        const response = await fetch(`${API_BASE}/voice/daily-summary?date=${today}&voice_type=en-US&speed=1.0`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const audio = new Audio(url);
            audio.play();
            showNotification('Voice summary generated', 'success');
        } else {
            throw new Error('Failed to generate voice summary');
        }
    } catch (error) {
        console.error('Error generating voice summary:', error);
        showNotification('Error generating voice summary', 'error');
    } finally {
        showLoading(false);
    }
}

// Send notifications
async function sendNotifications() {
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/notifications/daily-summary`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification(`Notifications sent: ${result.message}`, 'success');
        } else {
            throw new Error('Failed to send notifications');
        }
    } catch (error) {
        console.error('Error sending notifications:', error);
        showNotification('Error sending notifications', 'error');
    } finally {
        showLoading(false);
    }
}

// Mark email as read
async function markAsRead(emailId) {
    try {
        const response = await fetch(`${API_BASE}/emails/mark-read/${emailId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showNotification('Email marked as read', 'success');
            loadDashboardData(); // Refresh data
        }
    } catch (error) {
        console.error('Error marking email as read:', error);
        showNotification('Error marking email as read', 'error');
    }
}

// Mark email as replied
async function markAsReplied(emailId) {
    try {
        const response = await fetch(`${API_BASE}/emails/mark-replied/${emailId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showNotification('Email marked as replied', 'success');
            loadDashboardData(); // Refresh data
        }
    } catch (error) {
        console.error('Error marking email as replied:', error);
        showNotification('Error marking email as replied', 'error');
    }
}

// Settings functions
function openSettings() {
    document.getElementById('settingsModal').classList.remove('hidden');
    loadSettings();
}

function closeSettings() {
    document.getElementById('settingsModal').classList.add('hidden');
}

async function loadSettings() {
    try {
        // Load email config
        const emailResponse = await fetch(`${API_BASE}/config/email`);
        if (emailResponse.ok) {
            const emailConfig = await emailResponse.json();
            document.getElementById('emailAddress').value = emailConfig.email_address || '';
            document.getElementById('emailPassword').value = emailConfig.password || '';
        }
        
        // Load notification config
        const notificationResponse = await fetch(`${API_BASE}/notifications/config`);
        if (notificationResponse.ok) {
            const notificationConfig = await notificationResponse.json();
            document.getElementById('slackWebhook').value = notificationConfig.slack_webhook_url || '';
            document.getElementById('telegramToken').value = notificationConfig.telegram_bot_token || '';
            document.getElementById('telegramChatId').value = notificationConfig.telegram_chat_id || '';
        }
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

async function saveSettings() {
    showLoading(true);
    
    try {
        // Save email config
        const emailConfig = {
            email_address: document.getElementById('emailAddress').value,
            password: document.getElementById('emailPassword').value,
            imap_server: 'imap.gmail.com',
            imap_port: 993,
            smtp_server: 'smtp.gmail.com',
            smtp_port: 587,
            use_ssl: true,
            vip_contacts: [],
            auto_categorize: true,
            daily_summary_time: '09:00',
            response_reminder_hours: 24,
            follow_up_reminder_days: 3
        };
        
        await fetch(`${API_BASE}/config/email`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(emailConfig)
        });
        
        // Save notification config
        const notificationConfig = {
            slack_webhook_url: document.getElementById('slackWebhook').value,
            telegram_bot_token: document.getElementById('telegramToken').value,
            telegram_chat_id: document.getElementById('telegramChatId').value,
            whatsapp_webhook_url: '',
            enable_voice_summary: false,
            notification_channels: []
        };
        
        await fetch(`${API_BASE}/notifications/config`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(notificationConfig)
        });
        
        showNotification('Settings saved successfully', 'success');
        closeSettings();
    } catch (error) {
        console.error('Error saving settings:', error);
        showNotification('Error saving settings', 'error');
    } finally {
        showLoading(false);
    }
}

// Utility functions
function showLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    if (show) {
        spinner.classList.remove('hidden');
    } else {
        spinner.classList.add('hidden');
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        type === 'warning' ? 'bg-yellow-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    notification.textContent = message;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
} 