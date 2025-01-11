window.addEventListener('load', () => {
    const loadingScreen = document.getElementById('loading-screen');
    const mainContent = document.getElementById('main-content');

   
    setTimeout(() => {
        loadingScreen.style.display = 'none';
        mainContent.style.display = 'block';

        
        setTimeout(() => {
            mainContent.style.opacity = 1;
        }, 100);
    }, 2000); 
});

// upload submission wait JavaScript 0083
async function handleSubmit() {
    const imageInput = document.getElementById("imageUpload");
    const popup = document.getElementById("popup");
    const location = document.getElementById("itemSelector").value;
    const district = document.getElementById("districtSelector").value;

    if (!imageInput.files.length) {
        showPopup("😩 Please upload an image! 🤝", false);
        return;
    }

    if (!location || !district) {
        showPopup("Please select both location and district!", false);
        return;
    }

    const formData = new FormData();
    formData.append('image', imageInput.files[0]);
    formData.append('location', location);
    formData.append('district', district);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showPopup("✅ Successfully Uploaded! 🔥", true);
            updateDetectedPrices(data.data);
            updateMarketSummary(data.data);
        } else {
            showPopup(data.error || "Upload failed!", false);
        }
    } catch (error) {
        showPopup("Error uploading image!", false);
        console.error('Error:', error);
    }
}

function showPopup(message, success) {
    const popup = document.getElementById("popup");
    popup.textContent = message;
    popup.style.backgroundColor = success ? "#023020" : "#960100";
    popup.style.display = "block";

    setTimeout(() => {
        popup.style.display = "none";
    }, 3000);
}

function updateDetectedPrices(data) {
    const detectedPrices = document.getElementById("detectedPrices");
    if (!data || !data.length) {
        detectedPrices.innerHTML = "<p>No prices detected</p>";
        return;
    }

    let html = "<h3>Detected Prices:</h3><ul>";
    data.forEach(item => {
        html += `<li>${item.product}: ₹${item.price}</li>`;
    });
    html += "</ul>";
    detectedPrices.innerHTML = html;
}

function updateMarketSummary(data) {
    if (!data || !data.length) return;

    const summaryCards = document.querySelector(".summary-cards-container");
    summaryCards.innerHTML = ""; // Clear existing cards

    data.forEach(item => {
        const card = document.createElement("div");
        card.className = "summary-card";
        card.innerHTML = `
            <h3>${item.product}</h3>
            <p class="price">₹${item.price}</p>
        `;
        summaryCards.appendChild(card);
    });
}

// Toggle detected prices
function toggleDetectedPrices() {
    const detectedPrices = document.getElementById("detectedPrices");
    detectedPrices.style.display = detectedPrices.style.display === "block" ? "none" : "block";
}

// Initialize loading screen
window.addEventListener('load', () => {
    const loadingScreen = document.getElementById('loading-screen');
    setTimeout(() => {
        loadingScreen.style.display = 'none';
    }, 2000);
});

// Price 4552
const chartContainer = document.querySelector(".chart");
const selectElement = document.getElementById("itemSelector");

selectElement.addEventListener("change", () => {
    chartContainer.innerHTML = `Price history for ${selectElement.value}`;
});
