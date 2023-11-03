
const userRole = getUserRole();
const userTitleElement = document.getElementById('userTitle');

if (userRole === 'admin') {
    if (userTitleElement) {
        userTitleElement.textContent = 'Admin';
    }
} else if (userRole === 'user') {
    if (userTitleElement) {
        userTitleElement.textContent = 'User';
    }
}


// Function to retrieve the user role from sessionStorage
function getUserRole() {
    return sessionStorage.getItem('userRole');
}

// Function to perform access control based on the user's role
function performAccessControl() {
    const userRole = getUserRole();
    if (userRole === 'admin') {
        // Example: Show admin-specific content or features
        console.log('User is an admin');
    } else if (userRole === 'user') {
        // Example: Show user-specific content or features
        console.log('User is a regular user');
        // Hide the "users.html" link for regular users
        const usersLink = document.getElementById('usersLink');
        if (usersLink) {
            usersLink.style.display = 'none';
        }
    } else {
        // Handle other cases or roles
        console.log('User role not recognized');
    }

    const logoutLink = document.getElementById('logoutLink');
    if (logoutLink) {
        logoutLink.addEventListener('click', function (event) {
            event.preventDefault(); // Prevent the default behavior of the link
            logoutUser(); // You need to implement the logoutUser function
            // Redirect to "index.html"
            window.location.href = 'index.html';
        });
    }
}



// Function to perform access control based on the user's role


// Implement the function to log the user out (destroy the session)
function logoutUser() {
    // Clear the user role from sessionStorage
    sessionStorage.removeItem('userRole');
}
// Call the access control function when the page loads
document.addEventListener('DOMContentLoaded', performAccessControl);

