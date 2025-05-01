
  // --- GLOBAL VARIABLES ---
  const params = new URLSearchParams(window.location.search);
  const cookId = params.get("cook_id");

  if (!cookId) {
    alert("Cook ID not found.");
  }

  // --- THEME TOGGLE ---
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

  // --- INITIALIZE ON LOAD ---
  document.addEventListener("DOMContentLoaded", () => {
    // Theme init
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
      document.querySelector('.theme-toggle').textContent = '🌞 Light Mode';
    }

    if (!cookId) return;

    // Fetch cook profile
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

    // Fetch meals
    fetch(`http://127.0.0.1:5000/meals/${cookId}`)
      .then(res => res.json())
      .then(data => {
        const gallery = document.getElementById("mealGallery");
        gallery.innerHTML = "";

        data.meals.forEach(meal => {
          const card = document.createElement("div");
          card.className = "card";
          card.innerHTML = `
            <img src="data:image/jpeg;base64,${meal.image}" 
                 data-name="${meal.name}" 
                 data-price="${meal.price}" 
                 data-description="${meal.description}"
                 alt="${meal.name}">
          `;
          gallery.appendChild(card);
        });

        // Meal card click behavior
        let selectedImage = null;
        document.querySelectorAll('.gallery .card img').forEach(img => {
          img.addEventListener('click', () => {
            const mealImage = document.getElementById('mealImage');
            const mealPrice = document.getElementById('mealPrice');
            const mealDescription = document.getElementById('mealDescription');
            const mealName = document.getElementById('mealName');

            if (selectedImage === img) {
              mealImage.src = "";
              mealImage.alt = "";
              mealPrice.textContent = "";
              mealDescription.textContent = "";
              if (mealName) mealName.textContent = "";
              selectedImage = null;
            } else {
              mealImage.src = img.src;
              mealImage.alt = img.alt;
              mealPrice.textContent = img.dataset.price;
              mealDescription.textContent = img.dataset.description;
              if (mealName) mealName.textContent = img.alt;
              selectedImage = img;
            }
          });
        });
      })
      .catch(err => {
        console.error("Error fetching meals:", err);
      });

    // Show or hide "Add Meal" button based on session
    fetch('http://127.0.0.1:5000/check_session', {
      credentials: "include"
    })
      .then(res => res.json())
      .then(sessionData => {
        const addMealBtn = document.getElementById("addMealBtn");
        if (
          sessionData.logged_in &&
          sessionData.user_type === "cook" &&
          sessionData.user_id == cookId
        ) {
          addMealBtn.style.display = "block";
        } else {
          addMealBtn.style.display = "none";
        }

        // Optional: explicitly remove for customers
        if (sessionData.logged_in && sessionData.user_type === 'customer') {
          document.getElementById('addMealBtn')?.remove();
        }
      })
      .catch(err => {
        console.error("Error checking session:", err);
      });

    // Header scroll effect
    window.addEventListener('scroll', () => {
      const header = document.querySelector('header');
      header.classList.toggle('header-scrolled', window.scrollY > 50);
    });

    // Toggle meal form visibility
    document.getElementById("addMealBtn").addEventListener("click", () => {
      document.getElementById("addMealForm").classList.toggle("hidden");
    });

    // Submit new meal
    document.getElementById("mealUploadForm").addEventListener("submit", async (e) => {
      e.preventDefault();

      const form = e.target;
      const formData = new FormData();

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
          location.reload();
        } else {
          alert("Error adding meal: " + result.error);
        }
      } catch (err) {
        console.error("Upload failed:", err);
        alert("Failed to upload meal.");
      }
    });
  });
  function submitRating() {
    const ratingInput = document.getElementById("ratingInput");
    const ratingValue = parseInt(ratingInput.value, 10);
    const cookId = 1;  // The cook's ID, which can be dynamically set
    const customerId = 1;  // The customer's ID, which should be retrieved from session or user data
  
    if (ratingValue >= 1 && ratingValue <= 5) {
      // Prepare the data to send to the server
      const data = {
        customer_id: customerId,
        cook_id: cookId,
        rating_value: ratingValue
      };
  
      // Send the rating to the backend
      fetch('http://127.0.0.1:5000/submit_rating', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      })
      .then(response => response.json())
      .then(data => {
        if (data.message === "Rating submitted successfully!") {
          alert("Thank you for your rating!");
        } else {
          alert("Error: " + data.message);
        }
      })
      .catch(err => {
        console.error("Error submitting rating:", err);
        alert("An error occurred. Please try again.");
      });
  
      // Clear the rating input field
      ratingInput.value = '';
    } else {
      alert("Please enter a valid rating between 1 and 5.");
    }
  }
  