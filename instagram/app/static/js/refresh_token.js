// Function to refresh the access token using AJAX
// function refreshAccessToken(refreshToken) {
//     fetch('/refresh', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify({
//             refresh_token: refreshToken
//         })
//     })
//     .then(response => response.json())
//     .then(data => {
//         // Update access token dynamically
//         sessionStorage.setItem('access_token', data.access_token);
//         console.log('Access token refreshed:', data.access_token);
//     })
//     .catch(error => {
//         console.error('Error refreshing token:', error);
//     });
// }
