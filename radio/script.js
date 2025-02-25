const audio = new Audio();
const playPauseButton = document.getElementById("play-pause");
const prevButton = document.getElementById("prev");
const nextButton = document.getElementById("next");
const trackTitle = document.getElementById("track-title");
const playlist = document.getElementById("playlist");
const tracks = Array.from(playlist.querySelectorAll("li"));

let currentTrackIndex = 0;

// Load the first track
loadTrack(currentTrackIndex);

// Play/Pause functionality
playPauseButton.addEventListener("click", () => {
  if (audio.paused) {
    audio.play();
    playPauseButton.textContent = "⏸️";
  } else {
    audio.pause();
    playPauseButton.textContent = "▶️";
  }
});

// Previous track
prevButton.addEventListener("click", () => {
  currentTrackIndex = (currentTrackIndex - 1 + tracks.length) % tracks.length;
  loadTrack(currentTrackIndex);
});

// Next track
nextButton.addEventListener("click", () => {
  currentTrackIndex = (currentTrackIndex + 1) % tracks.length;
  loadTrack(currentTrackIndex);
});

// Load a track
function loadTrack(index) {
  const track = tracks[index];
  audio.src = track.getAttribute("data-src");
  trackTitle.textContent = track.textContent;
  audio.play();
  playPauseButton.textContent = "⏸️";
}

// Playlist item click
tracks.forEach((track, index) => {
  track.addEventListener("click", () => {
    currentTrackIndex = index;
    loadTrack(currentTrackIndex);
  });
});

// When a track ends, play the next one
audio.addEventListener("ended", () => {
  currentTrackIndex = (currentTrackIndex + 1) % tracks.length;
  loadTrack(currentTrackIndex);
});
