import { initializeApp } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-app.js";
import { getDatabase, ref, push, serverTimestamp } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-database.js";

// Firebase config
const firebaseConfig = {
    apiKey: "AIzaSyBC34gGsq31d_EOnJHnhLvLGfN0gtkhghU",
    authDomain: "accdetails-agri.firebaseapp.com",
    databaseURL: "https://accdetails-agri-default-rtdb.firebaseio.com",
    projectId: "accdetails-agri",
    storageBucket: "accdetails-agri.appspot.com",
    messagingSenderId: "1026187035894",
    appId: "1:1026187035894:web:30f31df97a6c5caf26d8d7"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const database = getDatabase(app);

// Form reference
const formRef = ref(database, "accounts");

// ✅ Popup function (top center)
function showPopup(message, isSuccess = true) {
    const popup = document.getElementById("popupMessage");
    popup.textContent = message;

    popup.style.position = "fixed";
    popup.style.top = "20px";
    popup.style.left = "50%";
    popup.style.transform = "translateX(-50%)";
    popup.style.background = isSuccess ? "#28a745" : "#dc3545"; // green/red
    popup.style.color = "#fff";
    popup.style.padding = "15px 25px";
    popup.style.borderRadius = "8px";
    popup.style.fontSize = "16px";
    popup.style.fontWeight = "500";
    popup.style.boxShadow = "0 4px 12px rgba(0,0,0,0.3)";
    popup.style.display = "block";
    popup.style.zIndex = "1000";

    // Hide after 3 sec
    setTimeout(() => {
        popup.style.display = "none";
    }, 3000);
}

// ✅ Auto-save form values in localStorage
const form = document.getElementById("accountForm");
const inputs = form.querySelectorAll("input, select");

// Save data on input
inputs.forEach(input => {
    input.addEventListener("input", () => {
        const formData = {};
        inputs.forEach(i => {
            formData[i.id] = i.value;
        });
        localStorage.setItem("accountFormData", JSON.stringify(formData));
    });
});

// Restore data on load with delay
window.addEventListener("load", () => {
    setTimeout(() => {
        const savedData = localStorage.getItem("accountFormData");
        if (savedData) {
            const formData = JSON.parse(savedData);
            inputs.forEach(i => {
                if (formData[i.id]) {
                    i.value = formData[i.id];
                }
            });
        }
    }, 1000); // ⏳ 1 second delay before restoring
});

// ✅ Form submission
form.addEventListener("submit", (event) => {
    event.preventDefault();

    // Collect field values
    const fullname = document.getElementById("fullname").value.trim();
    const mobile = document.getElementById("mobile").value.trim();
    const email = document.getElementById("email").value.trim();
    const role = document.getElementById("role").value;
    const language = document.getElementById("language").value;
    const nation = document.getElementById("nation").value.trim();
    const state = document.getElementById("state").value.trim();
    const district = document.getElementById("district").value.trim();
    const pincode = document.getElementById("pincode").value.trim();
    const farmsize = document.getElementById("farmsize").value;

    // ✅ Validation
    if (!fullname || !mobile || !email || !role || !language || !nation || !state || !district || !pincode || !farmsize) {
        showPopup("⚠️ Please fill in all fields before creating an account!", false);
        return;
    }

    // Data object
    const data = {
        fullname,
        mobile,
        email,
        role,
        language,
        nation,
        state,
        district,
        pincode,
        farmsize: Number(farmsize),
        createdAt: serverTimestamp()
    };

    // ✅ Save only when all fields are filled
    push(formRef, data)
        .then(() => {
            showPopup("✅ Successfully created an account!", true);

            // Clear form + localStorage
            form.reset();
            localStorage.removeItem("accountFormData");

            // ⏳ Redirect after 2 seconds so popup is visible
            setTimeout(() => {
                window.location.href = "home.html";
            }, 2000);

        })
        .catch((error) => {
            console.error("Error submitting form:", error);
            showPopup("❌ Failed to create account!", false);
        });
});