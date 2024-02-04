// Your existing code

// Add a function to get time-of-day recommendations
function getRecommendationsByTime() {
    $.ajax({
        url: '/get_time_of_day_recommendations',
        method: 'GET',
        success: function(data) {
            // Update the 'timeOfDayRecommendations' div with the received recommendations
            $('#timeOfDayRecommendations').html('<p>' + data.recommendations.join('</p><p>') + '</p>');
        },
        error: function(error) {
            console.error('Error fetching time-of-day recommendations:', error);
        }
    });
}

// Add a function to handle collaborative playlists
function inviteFriends() {
    $.ajax({
        url: '/invite_friends',
        method: 'GET',
        success: function(data) {
            // Update the 'collaborativePlaylist' div with the collaborative playlist information
            $('#collaborativePlaylist').html('<p>Playlist Name: ' + data.playlist_name + '</p><p>Contributors: ' + data.contributors.join(', ') + '</p>');
        },
        error: function(error) {
            console.error('Error inviting friends:', error);
        }
    });
}
