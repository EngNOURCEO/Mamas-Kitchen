let allCooks = [];  // Global array to store fetched cooks

fetch("http://127.0.0.1:5000/cooks")
  .then(response => response.json())
  .then(data => {
    console.log(data);
    allCooks = data.cooks; // Save all cooks
    renderCooks(allCooks); // Initial render
  })
  .catch(err => {
    console.error('Error fetching cooks:', err);
  });

function renderCooks(cooks) {
  const cardsContainer = document.getElementById('cards');
  cardsContainer.innerHTML = ''; // Clear previous content

  cooks.forEach(cook => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <h3>${cook.name}</h3>
      <p><strong>Gender:</strong> ${cook.gender}</p>
      <p><strong>Location:</strong> ${cook.location}</p>
      <button onclick="location.href='profile.html?cook_id=${cook.id}'">Show Profile</button>
    `;
    cardsContainer.appendChild(card);
  });
}

function filterByLocation() {
  const selected = document.getElementById('locationFilter').value;
  if (selected === 'all') {
    renderCooks(allCooks);
  } else {
    const filtered = allCooks.filter(cook => cook.location === selected);
    renderCooks(filtered);
  }
}

function toggleTheme() {
  const html = document.documentElement;
  const themeToggle = document.querySelector('.theme-toggle');

  if (html.getAttribute('data-theme') === 'dark') {
    html.removeAttribute('data-theme');
    themeToggle.textContent = '🌙 Dark Mode';
    localStorage.setItem('theme', 'light');
  } else {
    html.setAttribute('data-theme', 'dark');
    themeToggle.textContent = '🌞 Light Mode';
    localStorage.setItem('theme', 'dark');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem('theme') || 'light';
  const html = document.documentElement;
  const themeToggle = document.querySelector('.theme-toggle');

  if (savedTheme === 'dark') {
    html.setAttribute('data-theme', 'dark');
    themeToggle.textContent = '🌞 Light Mode';
  }
});
