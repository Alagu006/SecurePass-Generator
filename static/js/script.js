// static/js/script.js

// Tab navigation
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + '-tab').classList.add('active');
    event.target.classList.add('active');
}

// Check password strength
async function checkPassword() {
    const password = document.getElementById('passwordInput').value;
    if (!password) {
        alert('Please enter a password to check');
        return;
    }
    
    const loading = document.getElementById('checkLoading');
    const result = document.getElementById('checkResult');
    
    loading.style.display = 'block';
    result.style.display = 'none';
    
    // Simulate API call
    setTimeout(async () => {
        try {
            const formData = new FormData();
            formData.append('password', password);
            
            const response = await fetch('/check', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            // Display results
            document.getElementById('strengthDisplay').textContent = data.strength;
            document.getElementById('strengthDisplay').style.backgroundColor = getColor(data.strength_color);
            
            document.getElementById('crackTime').textContent = data.crack_time;
            document.getElementById('scoreDisplay').textContent = `${data.score}/${data.max_score}`;
            document.getElementById('lengthDisplay').textContent = data.length;
            
            const feedbackList = document.getElementById('feedbackList');
            feedbackList.innerHTML = '';
            
            data.feedback.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item;
                
                if (item.includes('✅') || item.includes('Excellent') || item.includes('Good') || item.includes('Not a commonly')) {
                    li.className = 'good';
                } else if (item.includes('⚠️') || item.includes('could be better')) {
                    li.className = 'warning';
                } else {
                    li.className = 'bad';
                }
                
                feedbackList.appendChild(li);
            });
            
            loading.style.display = 'none';
            result.style.display = 'block';
        } catch (error) {
            console.error('Error:', error);
            loading.style.display = 'none';
            alert('Error checking password. Please try again.');
        }
    }, 500);
}

// Generate password
async function generatePassword() {
    const length = document.getElementById('passwordLength').value;
    
    const loading = document.getElementById('generateLoading');
    const result = document.getElementById('generateResult');
    
    loading.style.display = 'block';
    result.style.display = 'none';
    
    setTimeout(async () => {
        try {
            const response = await fetch(`/generate?length=${length}`);
            const data = await response.json();
            
            document.getElementById('generatedPassword').textContent = data.password;
            
            // Show analysis if available
            if (data.analysis) {
                const analysisDiv = document.getElementById('generateAnalysis');
                analysisDiv.innerHTML = `
                    <h4>Auto-analysis:</h4>
                    <div class="strength-display" style="background-color: ${getColor(data.analysis.strength_color)}">
                        ${data.analysis.strength}
                    </div>
                    <p>Score: ${data.analysis.score}/${data.analysis.max_score}</p>
                `;
            }
            
            loading.style.display = 'none';
            result.style.display = 'block';
        } catch (error) {
            console.error('Error:', error);
            loading.style.display = 'none';
            alert('Error generating password. Please try again.');
        }
    }, 500);
}

// Hash password
async function hashPassword() {
    const password = document.getElementById('hashInput').value;
    if (!password) {
        alert('Please enter a password to hash');
        return;
    }
    
    const loading = document.getElementById('hashLoading');
    const result = document.getElementById('hashResult');
    
    loading.style.display = 'block';
    result.style.display = 'none';
    
    setTimeout(async () => {
        try {
            const formData = new FormData();
            formData.append('password', password);
            
            const response = await fetch('/hash', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            document.getElementById('originalPassword').textContent = data.password;
            document.getElementById('md5Hash').textContent = data.hashes.md5;
            document.getElementById('sha256Hash').textContent = data.hashes.sha256;
            document.getElementById('sha512Hash').textContent = data.hashes.sha512;
            document.getElementById('saltValue').textContent = data.salt;
            document.getElementById('saltedHash').textContent = data.salted_hash;
            
            loading.style.display = 'none';
            result.style.display = 'block';
        } catch (error) {
            console.error('Error:', error);
            loading.style.display = 'none';
            alert('Error hashing password. Please try again.');
        }
    }, 500);
}

// Check for breaches
async function checkBreach() {
    const password = document.getElementById('breachInput').value;
    if (!password) {
        alert('Please enter a password to check');
        return;
    }
    
    const loading = document.getElementById('breachLoading');
    const result = document.getElementById('breachResult');
    
    loading.style.display = 'block';
    result.style.display = 'none';
    
    setTimeout(async () => {
        try {
            const formData = new FormData();
            formData.append('password', password);
            
            const response = await fetch('/breach', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            const statusDiv = document.getElementById('breachStatus');
            const detailsDiv = document.getElementById('breachDetails');
            
            if (data.in_breach) {
                statusDiv.textContent = '⚠️ PASSWORD FOUND IN BREACHES!';
                statusDiv.style.backgroundColor = 'rgba(255, 0, 0, 0.3)';
                statusDiv.style.color = '#ff9999';
                
                detailsDiv.innerHTML = `
                    <p>This password is known to hackers from previous data breaches.</p>
                    <p>Found variations: ${data.found_variations.join(', ') || 'Exact match'}</p>
                    <p><strong>Immediate Action Required:</strong></p>
                    <ul class="feedback-list">
                        <li class="bad">Change this password everywhere you use it</li>
                        <li class="bad">Never reuse this password again</li>
                        <li class="bad">Consider using a password manager</li>
                    </ul>
                `;
            } else {
                statusDiv.textContent = '✅ Password not found in common breaches';
                statusDiv.style.backgroundColor = 'rgba(0, 255, 0, 0.2)';
                statusDiv.style.color = '#a0ffa0';
                
                detailsDiv.innerHTML = `
                    <p>Good news! This password doesn't appear in our common breach database.</p>
                    <p><strong>Note:</strong> This checks against known breach lists, but not all possible breaches.</p>
                    <p>Always practice good password hygiene:</p>
                    <ul class="feedback-list">
                        <li class="good">Use unique passwords for each site</li>
                        <li class="good">Enable two-factor authentication</li>
                        <li class="good">Regularly check haveibeenpwned.com</li>
                    </ul>
                `;
            }
            
            loading.style.display = 'none';
            result.style.display = 'block';
        } catch (error) {
            console.error('Error:', error);
            loading.style.display = 'none';
            alert('Error checking breaches. Please try again.');
        }
    }, 500);
}

// Helper function for colors
function getColor(colorName) {
    const colors = {
        'green': '#4CAF50',
        'blue': '#2196F3',
        'orange': '#FF9800',
        'red': '#f44336'
    };
    return colors[colorName] || '#4CAF50';
}

// Copy password to clipboard
function copyPassword() {
    const password = document.getElementById('generatedPassword').textContent;
    navigator.clipboard.writeText(password).then(() => {
        alert('Password copied to clipboard!');
    });
}

// Test generated password
function testGeneratedPassword() {
    const password = document.getElementById('generatedPassword').textContent;
    document.getElementById('passwordInput').value = password;
    showTab('check');
    setTimeout(() => checkPassword(), 100);
}

// Demo with example passwords
function loadExamples() {
    const examples = [
        "password123",
        "MySecurePass123!",
        "Xk7$pQ9@mN2&vL5",
        "iloveyou",
        "PurpleTiger-42-Mountains!"
    ];
    
    // Set first example in check tab
    document.getElementById('passwordInput').value = examples[0];
    
    // Set example in hash tab
    document.getElementById('hashInput').value = examples[1];
    
    // Set example in breach tab
    document.getElementById('breachInput').value = examples[3];
}

// Make functions available globally
window.showTab = showTab;
window.checkPassword = checkPassword;
window.generatePassword = generatePassword;
window.hashPassword = hashPassword;
window.checkBreach = checkBreach;
window.copyPassword = copyPassword;
window.testGeneratedPassword = testGeneratedPassword;

// Load examples when page loads
window.onload = loadExamples;