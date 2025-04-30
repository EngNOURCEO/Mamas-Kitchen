fetch("http://127.0.0.1:5000/cooks")
  .then(response => response.json())
  .then(data => {
    console.log(data);  // تحقق من البيانات في الـ console
    const cardsContainer = document.getElementById('cards');
    data.cooks.forEach(cook => {
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = `
        <h3>${cook.name}</h3>
        
        <p><strong>الجنس:</strong> ${cook.gender}</p>
        <p><strong>الموقع:</strong> ${cook.location}</p>
       
        <button onclick="location.href='profile.html?cook_id=${cook.id}'">عرض الملف الشخصي</button>
      `;
      cardsContainer.appendChild(card);
    });
  })
  .catch(err => {
    console.error('Error fetching cooks:', err);
  });
