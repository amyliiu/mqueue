document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('queueForm');
    const nameInput = document.getElementById('name');
    const phoneInput = document.getElementById('phone');
    const submitBtn = document.getElementById('submitBtn');
    const formPage = document.getElementById('form-page');
    const queuePage = document.getElementById('queue-page');
    const queueGrid = document.getElementById('queueGrid');

    // Enable/disable submit button based on form validity
    function validateForm() {
        const isValid = nameInput.value.trim() !== '' && 
                       phoneInput.value.trim() !== '' &&
                       document.getElementById('consent').checked;
        submitBtn.disabled = !isValid;
    }

    // Add event listeners for real-time validation
    nameInput.addEventListener('input', validateForm);
    phoneInput.addEventListener('input', validateForm);
    document.getElementById('consent').addEventListener('change', validateForm);

    // Handle form submission
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const userName = nameInput.value.trim();
        
        // Generate random queue position (1-10 for demo)
        const queuePosition = Math.floor(Math.random() * 10) + 1;
        
        // Switch to queue page
        formPage.style.display = 'none';
        queuePage.style.display = 'block';
        
        // Update queue number
        document.querySelector('.queue-number').textContent = 
            `${queuePosition}${getNumberSuffix(queuePosition)}`;
        
        // Generate queue items
        generateQueueItems(userName, 12); // Display 12 queue items
    });
});

// Generate suffix for numbers (1st, 2nd, 3rd, etc.)
function getNumberSuffix(number) {
    const j = number % 10;
    const k = number % 100;
    if (j == 1 && k != 11) return "st";
    if (j == 2 && k != 12) return "nd";
    if (j == 3 && k != 13) return "rd";
    return "th";
}

// Generate queue items with random names
function generateQueueItems(userName, count) {
    const names = [
        'John', 'Jane', 'Alex', 'Sarah', 'Mike', 'Emma', 
        'David', 'Lisa', 'Tom', 'Anna', 'Chris', 'Maria'
    ];
    
    const queueGrid = document.getElementById('queueGrid');
    queueGrid.innerHTML = ''; // Clear existing items
    
    for (let i = 0; i < count; i++) {
        const div = document.createElement('div');
        div.className = 'queue-item';
        
        // Randomly insert user's name, make it highlighted
        if (Math.random() < 0.3 || i === 0) { // 30% chance or first item
            div.textContent = userName;
            div.className += ' current';
        } else {
            const randomName = names[Math.floor(Math.random() * names.length)];
            div.textContent = randomName;
        }
        
        queueGrid.appendChild(div);
    }
}
