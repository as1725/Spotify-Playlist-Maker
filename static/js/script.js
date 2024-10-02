document.getElementById("login-button").addEventListener("click", function () {
	window.location.href = "/";
});

document.addEventListener("DOMContentLoaded", function () {
	console.log("DOM fully loaded and parsed");
	fetch("/is_authenticated")
		.then((response) => {
			console.log("Received response from /is_authenticated", response);
			return response.json();
		})
		.then((data) => {
			console.log("Parsed JSON data", data);
			if (data.authenticated) {
				console.log("User is authenticated, revealing form");
				document.getElementById("playlist-form").classList.remove("hidden");
				document.getElementById("logout-button").classList.remove("hidden");
				document.getElementById("login-button").classList.add("hidden");

				document.getElementById("user-name").textContent = data.user_name;
				document.getElementById("user-info").classList.remove("hidden");
			} else {
				console.log("User is not authenticated");
				document.getElementById("logout-button").classList.add("hidden");
				document.getElementById("login-button").classList.remove("hidden");
			}
		})
		.catch((error) => {
			showAlert("Error fetching /is_authenticated: " + error.message);
		});
});

document.getElementById("logout-button").addEventListener("click", function () {
	fetch("/logout")
		.then(() => {
			console.log("Logged out successfully");
			const url = "https://accounts.spotify.com/en/logout";
			const spotifyLogoutWindow = window.open(
				url,
				"Spotify Logout",
				"width=700,height=500,top=40,left=40"
			);
			setTimeout(() => {
				spotifyLogoutWindow.close();
				window.location.href = "/";
			}, 1000);
			document.getElementById("logout-button").classList.add("hidden");
			document.getElementById("login-button").classList.remove("hidden");
			document.getElementById("playlist-form").classList.add("hidden");

			document.getElementById("user-info").classList.add("hidden");
		})
		.catch((error) => {
			showAlert("Error logging out: " + error.message);
		});
});

document.getElementById("add-song").addEventListener("click", function () {
	const inputFields = document.getElementById("input-fields");
	const songInput = document.createElement("input");
	songInput.placeholder = "Enter song name";
	songInput.className = "song-input";
	inputFields.appendChild(songInput);

	const artistInput = document.createElement("input");
	artistInput.placeholder = "Enter artist name (optional)";
	artistInput.className = "artist-input";
	inputFields.appendChild(artistInput);
});

document
	.getElementById("submit-playlist")
	.addEventListener("click", async function () {
		const loader = document.getElementById("loader");
		loader.classList.remove("hidden");

		const songs = Array.from(document.querySelectorAll(".song-input")).map(
			(input, index) => ({
				song: input.value,
				artist: document.querySelectorAll(".artist-input")[index].value,
			})
		);

		const bulkSongs = document.getElementById("bulk-songs").value;
		if (bulkSongs) {
			const bulkSongsArray = bulkSongs
				.split(/\n|,/)
				.map((entry) => {
					const [song, artist] = entry.split(/by|-/).map((str) => str.trim());
					return { song, artist: artist || "" };
				})
				.filter((entry) => entry.song);
			songs.push(...bulkSongsArray);
		}

		const playlistName = document.getElementById("playlist-name").value;

		try {
			const response = await fetch("/create_playlist", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ songs, playlistName }),
			});

			const data = await response.json();
			if (data.playlistUrl) {
				document.getElementById("link").href = data.playlistUrl;
				document.getElementById("playlist-link").classList.remove("hidden");
				document.getElementById("playlist-form").classList.add("hidden");
			} else if (data.error) {
				showAlert(data.error);
			}
		} catch (error) {
			showAlert("Error creating playlist: " + error.message);
		} finally {
			loader.classList.add("hidden");
		}
	});

function showAlert(message) {
	const alertContainer = document.getElementById("alert-container");
	alertContainer.textContent = message;
	alertContainer.classList.remove("hidden");
	setTimeout(() => {
		alertContainer.classList.add("hidden");
	}, 5000);
}
