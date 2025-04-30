document.addEventListener("DOMContentLoaded", () => {
  // Fetch the cook's ID from the URL query parameters
  const params = new URLSearchParams(window.location.search);
  const cookId = params.get("cook_id");

  if (!cookId) {
    alert("Cook ID not found.");
    return;
  }

  // Fetch cook profile from the backend
  fetch(`http://127.0.0.1:5000/cooks/${cookId}`)
    .then(res => res.json())
    .then(data => {
      const cook = data.cook;
      document.getElementById("profileImage").src = cook.profile_image || "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSvlkjZjVftvitbZqo3RUajrYxfFJz7DZSn_w&s";
      document.getElementById("cookName").textContent = cook.name;
      document.getElementById("cookEmail").textContent = cook.email;
      document.getElementById("cookLocation").textContent = cook.location;
      document.getElementById("cookPhone").textContent = cook.phone;
    })
    .catch(err => {
      console.error("Error fetching cook profile:", err);
    });

  // Fetch meals for the cook (if needed)
  fetch(`http://127.0.0.1:5000/meals/${cookId}`)

    .then(res => res.json())
    .then(data => {
      const gallery = document.getElementById("mealGallery");
      gallery.innerHTML = ""; // Clear existing meal cards

      data.meals.forEach(meal => {
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `
          <img src="data:image/jpeg;base64,${meal.image}" alt="${meal.name}" data-price="${meal.price}" data-description="${meal.description}">
        `;
        gallery.appendChild(card);
      });

      // Event listener for meal card clicks
      document.querySelectorAll('.gallery .card img').forEach(img => {
        img.addEventListener('click', () => {
          const mealImage = document.getElementById('mealImage');
          const mealPrice = document.getElementById('mealPrice');
          const mealDescription = document.getElementById('mealDescription');
      
          mealImage.src = img.src;
          mealImage.alt = img.alt;
          mealPrice.textContent = img.dataset.price;
          mealDescription.textContent = img.dataset.description;
        });
      });
    })
    .catch(err => {
      console.error("Error fetching meals:", err);
    });
});
document.getElementById("addMealBtn").addEventListener("click", () => {
  document.getElementById("addMealForm").classList.toggle("hidden");
});

document.getElementById("mealUploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const form = e.target;
  const formData = new FormData();

  const params = new URLSearchParams(window.location.search);
  const cookId = params.get("cook_id");

  formData.append("meal_name", form.mealName.value);
  formData.append("meal_price", form.mealPrice.value);
  formData.append("recipe", form.mealDescription.value);
  formData.append("image", form.mealImageUpload.files[0]);
  formData.append("cook_id", cookId);

  try {
    const res = await fetch("http://127.0.0.1:5000/add_meal", {
      method: "POST",
      body: formData
    });

    const result = await res.json();
    if (result.success) {
      alert("Meal added successfully!");
      location.reload(); // Refresh to show the new meal
    } else {
      alert("Error adding meal: " + result.error);
    }
  } catch (err) {
    console.error("Upload failed:", err);
    alert("Failed to upload meal.");
  }
});



